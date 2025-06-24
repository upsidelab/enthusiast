from django.db.models import Count
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.generics import ListAPIView, ListCreateAPIView, GenericAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from account.models import User
from account.serializers import UserSerializer
from pecl import settings
from sync.tasks import (
    sync_all_sources,
    sync_all_document_sources,
    sync_data_set_all_sources,
    sync_data_set_document_sources,
    sync_document_source,
    sync_all_product_sources,
    sync_data_set_product_sources,
    sync_product_source,
)
from agent.registries.embeddings import EmbeddingProviderRegistry
from agent.registries.language_models import LanguageModelRegistry
from .models import DataSet, DocumentSource, ProductSource
from .serializers import (
    DataSetSerializer,
    DocumentSerializer,
    DocumentSourceSerializer,
    ProductSerializer,
    ProductSourceSerializer,
)


class SyncAllSourcesView(GenericAPIView):
    permission_classes = [IsAdminUser]

    def post(self, request, *args, **kwargs):
        task = sync_all_sources.apply_async()

        return Response({"task_id": task.id}, status=status.HTTP_202_ACCEPTED)


class DataSetListView(ListCreateAPIView):
    serializer_class = DataSetSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(operation_description="List data sets", manual_parameters=[])
    def get_queryset(self):
        if self.request.user and self.request.user.is_staff:
            return DataSet.objects.all()

        return DataSet.objects.filter(users=self.request.user)

    @swagger_auto_schema(operation_description="Create a new data set", request_body=DataSetSerializer)
    def perform_create(self, serializer):
        if not self.request.user and self.request.user.is_staff:
            self.permission_denied(self.request)

        data_set = serializer.save()
        data_set.users.add(self.request.user)


class DataSetUserListView(ListCreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]

    @swagger_auto_schema(
        operation_description="List users in a data set",
        manual_parameters=[
            openapi.Parameter(
                "data_set_id", openapi.IN_PATH, description="ID of the data set", type=openapi.TYPE_INTEGER
            )
        ],
    )
    def get_queryset(self):
        return DataSet.objects.get(id=self.kwargs["data_set_id"]).users.all()

    @swagger_auto_schema(
        operation_description="Add a user to a data set",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={"user_id": openapi.Schema(type=openapi.TYPE_INTEGER, description="ID of the user")},
        ),
    )
    def create(self, *args, **kwargs):
        user = User.objects.get(id=self.request.data["user_id"])
        DataSet.objects.get(id=self.kwargs["data_set_id"]).users.add(user)
        return Response({}, status=status.HTTP_201_CREATED)


class DataSetUserView(GenericAPIView):
    permission_classes = [IsAdminUser]

    @swagger_auto_schema(
        operation_description="Remove a user from a data set",
        manual_parameters=[
            openapi.Parameter(
                "data_set_id", openapi.IN_PATH, description="ID of the data set", type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter("user_id", openapi.IN_PATH, description="ID of the user", type=openapi.TYPE_INTEGER),
        ],
    )
    def delete(self, *args, **kwargs):
        DataSet.objects.get(id=self.kwargs["data_set_id"]).users.remove(self.kwargs["user_id"])
        return Response({}, status=status.HTTP_204_NO_CONTENT)


class SyncDataSetAllSourcesView(GenericAPIView):
    permission_classes = [IsAdminUser]

    def post(self, request, *args, **kwargs):
        task = sync_data_set_all_sources.apply_async(args=[kwargs["data_set_id"]])

        return Response({"task_id": task.id}, status=status.HTTP_202_ACCEPTED)


class DataSetProductSourceListView(ListCreateAPIView):
    serializer_class = ProductSourceSerializer
    permission_classes = [IsAdminUser]

    @swagger_auto_schema(
        operation_description="List product sources in a data set",
        manual_parameters=[
            openapi.Parameter(
                "data_set_id", openapi.IN_PATH, description="ID of the data set", type=openapi.TYPE_INTEGER
            )
        ],
    )
    def get_queryset(self):
        return ProductSource.objects.filter(data_set_id=self.kwargs["data_set_id"])

    @swagger_auto_schema(
        operation_description="Create a new product source in a data set", request_body=ProductSourceSerializer
    )
    def perform_create(self, serializer):
        if not self.request.user and self.request.user.is_staff:
            self.permission_denied(self.request)
        # Get data set from URL (it's not passed via request body).
        data_set_id = self.kwargs.get("data_set_id")
        serializer.save(data_set_id=data_set_id)


class DataSetProductSourceView(GenericAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = ProductSourceSerializer

    @swagger_auto_schema(
        operation_description="Retrieve a product source",
        manual_parameters=[
            openapi.Parameter(
                "data_set_id", openapi.IN_PATH, description="ID of the data set", type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                "product_source_id", openapi.IN_PATH, description="ID of the product source", type=openapi.TYPE_INTEGER
            ),
        ],
    )
    def get(self, request, data_set_id, product_source_id):
        product_source = ProductSource.objects.get(id=product_source_id)
        serializer = self.serializer_class(product_source)
        return Response(serializer.data)

    @swagger_auto_schema(operation_description="Update a product source", request_body=ProductSourceSerializer)
    def patch(self, request, *args, **kwargs):
        product_source = ProductSource.objects.get(id=kwargs.get("product_source_id"))
        product_source.plugin_name = request.data.get("plugin_name", product_source.plugin_name)
        product_source.config = request.data.get("config", product_source.config)
        product_source.data_set_id = request.data.get("data_set_id", product_source.data_set_id)
        product_source.save()

        serializer = self.serializer_class(product_source)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Delete a product source",
        manual_parameters=[
            openapi.Parameter(
                "data_set_id", openapi.IN_PATH, description="ID of the data set", type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                "product_source_id", openapi.IN_PATH, description="ID of the product source", type=openapi.TYPE_INTEGER
            ),
        ],
    )
    def delete(self, *args, **kwargs):
        ProductSource.objects.filter(id=kwargs["product_source_id"]).delete()
        return Response({}, status=status.HTTP_204_NO_CONTENT)


class SyncAllProductSourcesView(GenericAPIView):
    permission_classes = [IsAdminUser]

    def post(self, request, *args, **kwargs):
        task = sync_all_product_sources.apply_async()

        return Response({"task_id": task.id}, status=status.HTTP_202_ACCEPTED)


class SyncDataSetProductSourcesView(GenericAPIView):
    permission_classes = [IsAdminUser]

    def post(self, request, *args, **kwargs):
        task = sync_data_set_product_sources.apply_async(args=[kwargs["data_set_id"]])

        return Response({"task_id": task.id}, status=status.HTTP_202_ACCEPTED)


class SyncDataSetProductSourceView(GenericAPIView):
    permission_classes = [IsAdminUser]

    def post(self, request, *args, **kwargs):
        task = sync_product_source.apply_async(args=[kwargs["product_source_id"]])

        return Response({"task_id": task.id}, status=status.HTTP_202_ACCEPTED)


class ProductListView(ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination

    @swagger_auto_schema(
        operation_description="List products in a data set",
        manual_parameters=[
            openapi.Parameter(
                "data_set_id", openapi.IN_PATH, description="ID of the data set", type=openapi.TYPE_INTEGER
            )
        ],
    )
    def get_queryset(self):
        if self.request.user.is_staff:
            data_set = DataSet.objects.get(id=self.kwargs["data_set_id"])
        else:
            data_set = DataSet.objects.get(id=self.kwargs["data_set_id"], users=self.request.user)
        return data_set.products.all()


class DocumentListView(ListAPIView):
    serializer_class = DocumentSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination

    @swagger_auto_schema(
        operation_description="List documents in a data set",
        manual_parameters=[
            openapi.Parameter(
                "data_set_id", openapi.IN_PATH, description="ID of the data set", type=openapi.TYPE_INTEGER
            )
        ],
    )
    def get_queryset(self):
        if self.request.user.is_staff:
            data_set = DataSet.objects.get(id=self.kwargs["data_set_id"])
        else:
            data_set = DataSet.objects.get(id=self.kwargs["data_set_id"], users=self.request.user)
        return data_set.documents.annotate(chunks_count=Count("chunks")).all()


class DataSetDocumentSourceListView(ListCreateAPIView):
    serializer_class = DocumentSourceSerializer
    permission_classes = [IsAdminUser]

    @swagger_auto_schema(
        operation_description="List document sources in a data set",
        manual_parameters=[
            openapi.Parameter(
                "data_set_id", openapi.IN_PATH, description="ID of the data set", type=openapi.TYPE_INTEGER
            )
        ],
    )
    def get_queryset(self):
        return DocumentSource.objects.filter(data_set_id=self.kwargs["data_set_id"])

    @swagger_auto_schema(
        operation_description="Create a new document source in a data set", request_body=DocumentSourceSerializer
    )
    def perform_create(self, serializer):
        if not self.request.user and self.request.user.is_staff:
            self.permission_denied(self.request)
        # Get data set from URL (it's not passed via request body).
        data_set_id = self.kwargs.get("data_set_id")
        serializer.save(data_set_id=data_set_id)


class DataSetDocumentSourceView(GenericAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = DocumentSourceSerializer

    @swagger_auto_schema(
        operation_description="Retrieve a document source",
        manual_parameters=[
            openapi.Parameter(
                "data_set_id", openapi.IN_PATH, description="ID of the data set", type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                "document_source_id",
                openapi.IN_PATH,
                description="ID of the document source",
                type=openapi.TYPE_INTEGER,
            ),
        ],
    )
    def get(self, request, data_set_id, document_source_id):
        document_source = DocumentSource.objects.get(id=document_source_id)
        serializer = self.serializer_class(document_source)
        return Response(serializer.data)

    @swagger_auto_schema(operation_description="Update a document source", request_body=DocumentSourceSerializer)
    def patch(self, request, *args, **kwargs):
        document_source = DocumentSource.objects.get(id=kwargs.get("document_source_id"))
        document_source.plugin_name = request.data.get("plugin_name", document_source.plugin_name)
        document_source.config = request.data.get("config", document_source.config)
        document_source.data_set_id = request.data.get("data_set_id", document_source.data_set_id)
        document_source.save()

        serializer = self.serializer_class(document_source)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Delete a document source",
        manual_parameters=[
            openapi.Parameter(
                "data_set_id", openapi.IN_PATH, description="ID of the data set", type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                "document_source_id",
                openapi.IN_PATH,
                description="ID of the document source",
                type=openapi.TYPE_INTEGER,
            ),
        ],
    )
    def delete(self, *args, **kwargs):
        DocumentSource.objects.filter(id=kwargs["document_source_id"]).delete()
        return Response({}, status=status.HTTP_204_NO_CONTENT)


class SyncAllDocumentSourcesView(GenericAPIView):
    permission_classes = [IsAdminUser]

    def post(self, request, *args, **kwargs):
        task = sync_all_document_sources.apply_async()

        return Response({"task_id": task.id}, status=status.HTTP_202_ACCEPTED)


class SyncDataSetDocumentSourcesView(GenericAPIView):
    permission_classes = [IsAdminUser]

    def post(self, request, *args, **kwargs):
        task = sync_data_set_document_sources.apply_async(args=[kwargs["data_set_id"]])

        return Response({"task_id": task.id}, status=status.HTTP_202_ACCEPTED)


class SyncDataSetDocumentSourceView(GenericAPIView):
    permission_classes = [IsAdminUser]

    def post(self, request, *args, **kwargs):
        task = sync_document_source.apply_async(args=[kwargs["document_source_id"]])

        return Response({"task_id": task.id}, status=status.HTTP_202_ACCEPTED)


class ConfigView(GenericAPIView):
    permission_classes = [IsAdminUser]

    def get(self, request, *args, **kwargs):
        response_body = {
            "language_model_providers": settings.CATALOG_LANGUAGE_MODEL_PROVIDERS.keys(),
            "embedding_providers": settings.CATALOG_EMBEDDING_PROVIDERS.keys(),
        }

        return Response(response_body)


class ConfigLanguageModelView(GenericAPIView):
    permission_classes = [IsAdminUser]

    def get(self, request, *args, **kwargs):
        provider_name = kwargs.get("provider_name")
        response_body = LanguageModelRegistry().provider_class_by_name(provider_name).available_models()

        return Response(response_body)


class ConfigEmbeddingModelView(GenericAPIView):
    permission_classes = [IsAdminUser]

    def get(self, request, *args, **kwargs):
        provider_name = kwargs.get("provider_name")
        response_body = EmbeddingProviderRegistry().provider_class_by_name(provider_name).available_models()

        return Response(response_body)
