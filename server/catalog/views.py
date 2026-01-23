from django.conf import settings
from django.db import transaction
from django.db.models import Count
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.generics import GenericAPIView, ListAPIView, ListCreateAPIView, RetrieveAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from utils.functions import get_model_descriptor_default_value_from_class

from account.models import User
from account.serializers import UserSerializer
from agent.core.registries.agents.agent_registry import AgentRegistry
from agent.core.registries.embeddings import EmbeddingProviderRegistry
from agent.core.registries.language_models import LanguageModelRegistry
from agent.models import Agent
from sync.tasks import (
    sync_all_document_sources,
    sync_all_product_sources,
    sync_all_sources,
    sync_data_set_all_sources,
    sync_data_set_document_sources,
    sync_data_set_product_sources,
    sync_document_source,
    sync_ecommerce_integration,
    sync_ecommerce_integrations,
    sync_product_source,
)

from .models import DataSet, DocumentSource, ECommerceIntegration, ProductSource
from .serializers import (
    DataSetCreateSerializer,
    DataSetSerializer,
    DocumentSerializer,
    DocumentSourceSerializer,
    ECommerceIntegrationSerializer,
    ProductSerializer,
    ProductSourceSerializer,
    SyncResponseSerializer,
)


class SyncAllSourcesView(APIView):
    permission_classes = [IsAdminUser]

    @swagger_auto_schema(
        operation_description="Sync all sources",
        responses={200: SyncResponseSerializer},
    )
    def post(self, request, *args, **kwargs):
        task = sync_all_sources.apply_async()
        serializer = SyncResponseSerializer({"task_id": task.id})
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)


class DataSetListView(ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return DataSetCreateSerializer
        return DataSetSerializer


    @swagger_auto_schema(operation_description="List data sets")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        if self.request.user and self.request.user.is_staff:
            return DataSet.objects.all()

        return DataSet.objects.filter(users=self.request.user)

    @swagger_auto_schema(operation_description="Create a new data set", request_body=DataSetCreateSerializer)
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def perform_create(self, serializer):
        if not self.request.user.is_staff:
            self.permission_denied(self.request)

        with transaction.atomic():
            preconfigure_agents = serializer.validated_data.pop("preconfigure_agents", False)
            data_set = serializer.save()
            data_set.users.add(self.request.user)
            if preconfigure_agents:
                self.create_available_agents(data_set)

    @staticmethod
    def create_available_agents(data_set: DataSet):
        registry = AgentRegistry()

        for agent_type, agent_details in settings.AVAILABLE_AGENTS.items():
            if Agent.all_objects.filter(dataset=data_set, agent_type=agent_type).exists():
                continue

            agent_class = registry.get_agent_class_by_type(agent_type=agent_type)

            agent_configuration = {
                "agent_args": get_model_descriptor_default_value_from_class(agent_class, "AGENT_ARGS"),
                "prompt_input": get_model_descriptor_default_value_from_class(agent_class, "PROMPT_INPUT"),
                "prompt_extension": get_model_descriptor_default_value_from_class(agent_class, "PROMPT_EXTENSION"),
                "tools": [
                    get_model_descriptor_default_value_from_class(tool_config.tool_class, "CONFIGURATION_ARGS")
                    for tool_config in agent_class.TOOLS
                ],
            }

            Agent.objects.create(
                **{
                    "name": agent_details["name"],
                    "description": agent_details.get("description", ''),
                    "config": agent_configuration,
                    "dataset": data_set,
                    "agent_type": agent_type,
                })


class DataSetDetailView(RetrieveAPIView):
    serializer_class = DataSetSerializer
    permission_classes = [IsAdminUser]
    lookup_url_kwarg = "data_set_id"
    queryset = DataSet.objects.all()

    @swagger_auto_schema(
        operation_description="Retrieve a data set by ID",
        manual_parameters=[
            openapi.Parameter(
                "data_set_id", openapi.IN_PATH, description="ID of the data set", type=openapi.TYPE_INTEGER
            )
        ],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Update a data set (embedding fields are ignored)",
        request_body=DataSetSerializer,
        manual_parameters=[
            openapi.Parameter(
                "data_set_id", openapi.IN_PATH, description="ID of the data set", type=openapi.TYPE_INTEGER
            )
        ],
    )
    def patch(self, request, *args, **kwargs):
        instance = self.get_object()

        # Filter out embedding fields from the request data
        filtered_data = {
            k: v
            for k, v in request.data.items()
            if k not in ["embedding_provider", "embedding_model", "embedding_vector_dimensions"]
        }

        serializer = self.get_serializer(instance, data=filtered_data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)


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
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return DataSet.objects.get(id=self.kwargs["data_set_id"]).users.all()

    @swagger_auto_schema(
        operation_description="Add a user to a data set",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={"user_id": openapi.Schema(type=openapi.TYPE_INTEGER, description="ID of the user")},
        ),
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

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


class SyncDataSetAllSourcesView(APIView):
    permission_classes = [IsAdminUser]

    @swagger_auto_schema(
        operation_description="Sync all sources in a data set",
        responses={200: SyncResponseSerializer},
    )
    def post(self, request, *args, **kwargs):
        task = sync_data_set_all_sources.apply_async(args=[kwargs["data_set_id"]])
        serializer = SyncResponseSerializer({"task_id": task.id})
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)


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
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return ProductSource.objects.filter(data_set_id=self.kwargs["data_set_id"])

    @swagger_auto_schema(
        operation_description="Create a new product source in a data set", request_body=ProductSourceSerializer
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        task_id = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        response_data = dict(serializer.data)
        response_data["task_id"] = task_id
        return Response(response_data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        # Get data set from URL (it's not passed via request body).
        data_set_id = self.kwargs.get("data_set_id")
        source = serializer.save(data_set_id=data_set_id)
        task = sync_product_source.apply_async(args=[source.id])
        return task.id


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
        serializer = self.serializer_class(product_source, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(corrupted=False)

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


class SyncAllProductSourcesView(APIView):
    permission_classes = [IsAdminUser]

    @swagger_auto_schema(
        operation_description="Sync all product sources",
        responses={200: SyncResponseSerializer},
    )
    def post(self, request, *args, **kwargs):
        task = sync_all_product_sources.apply_async()
        serializer = SyncResponseSerializer({"task_id": task.id})
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)


class SyncDataSetProductSourcesView(APIView):
    permission_classes = [IsAdminUser]

    @swagger_auto_schema(
        operation_description="Sync all product sources in a data set",
        responses={200: SyncResponseSerializer},
    )
    def post(self, request, *args, **kwargs):
        task = sync_data_set_product_sources.apply_async(args=[kwargs["data_set_id"]])
        serializer = SyncResponseSerializer({"task_id": task.id})
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)


class SyncDataSetProductSourceView(APIView):
    permission_classes = [IsAdminUser]

    @swagger_auto_schema(
        operation_description="Sync a product source",
        responses={200: SyncResponseSerializer},
    )
    def post(self, request, *args, **kwargs):
        task = sync_product_source.apply_async(args=[kwargs["product_source_id"]])
        serializer = SyncResponseSerializer({"task_id": task.id})
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)


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
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

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
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

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
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return DocumentSource.objects.filter(data_set_id=self.kwargs["data_set_id"])

    @swagger_auto_schema(
        operation_description="Create a new document source in a data set", request_body=DocumentSourceSerializer
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def perform_create(self, serializer):
        # Get data set from URL (it's not passed via request body).
        data_set_id = self.kwargs.get("data_set_id")
        source = serializer.save(data_set_id=data_set_id)
        task = sync_document_source.apply_async(args=[source.id])
        return task.id

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        task_id = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        response_data = dict(serializer.data)
        response_data["task_id"] = task_id
        return Response(response_data, status=status.HTTP_201_CREATED, headers=headers)


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
        serializer = self.serializer_class(document_source, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(corrupted=False)
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


class SyncAllDocumentSourcesView(APIView):
    permission_classes = [IsAdminUser]

    @swagger_auto_schema(
        operation_description="Sync all document sources",
        responses={200: SyncResponseSerializer},
    )
    def post(self, request, *args, **kwargs):
        task = sync_all_document_sources.apply_async()
        serializer = SyncResponseSerializer({"task_id": task.id})
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)


class SyncDataSetDocumentSourcesView(APIView):
    permission_classes = [IsAdminUser]

    @swagger_auto_schema(
        operation_description="Sync all document sources in a data set",
        responses={200: SyncResponseSerializer},
    )
    def post(self, request, *args, **kwargs):
        task = sync_data_set_document_sources.apply_async(args=[kwargs["data_set_id"]])
        serializer = SyncResponseSerializer({"task_id": task.id})
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)


class SyncDataSetDocumentSourceView(APIView):
    permission_classes = [IsAdminUser]

    @swagger_auto_schema(
        operation_description="Sync a document source",
        responses={200: SyncResponseSerializer},
    )
    def post(self, request, *args, **kwargs):
        task = sync_document_source.apply_async(args=[kwargs["document_source_id"]])
        serializer = SyncResponseSerializer({"task_id": task.id})
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)


class DataSetECommerceIntegrationView(GenericAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = ECommerceIntegrationSerializer

    @swagger_auto_schema(
        operation_description="Get the ecommerce integration for a data set",
        manual_parameters=[
            openapi.Parameter(
                "data_set_id", openapi.IN_PATH, description="ID of the data set", type=openapi.TYPE_INTEGER
            )
        ],
    )
    def get(self, request, *args, **kwargs):
        data_set_id = kwargs["data_set_id"]
        try:
            ecommerce_integration = ECommerceIntegration.objects.get(data_set_id=data_set_id)
        except ECommerceIntegration.DoesNotExist:
            return Response({}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(ecommerce_integration)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Create an ecommerce integration for a data set",
        request_body=ECommerceIntegrationSerializer,
        manual_parameters=[
            openapi.Parameter(
                "data_set_id", openapi.IN_PATH, description="ID of the data set", type=openapi.TYPE_INTEGER
            )
        ],
    )
    def post(self, request, *args, **kwargs):
        data_set_id = kwargs["data_set_id"]

        if ECommerceIntegration.objects.filter(data_set_id=data_set_id).exists():
            return Response(
                {"error": "Ecommerce integration already exists for this data set"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ecommerce_integration = serializer.save(data_set_id=data_set_id)
        task = sync_ecommerce_integration.apply_async(args=[ecommerce_integration.id])
        response_data = dict(serializer.data)
        response_data["task_id"] = task.task_id
        return Response(response_data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        operation_description="Update the ecommerce integration for a data set",
        request_body=ECommerceIntegrationSerializer,
        manual_parameters=[
            openapi.Parameter(
                "data_set_id", openapi.IN_PATH, description="ID of the data set", type=openapi.TYPE_INTEGER
            )
        ],
    )
    def patch(self, request, *args, **kwargs):
        data_set_id = kwargs["data_set_id"]
        try:
            ecommerce_integration = ECommerceIntegration.objects.get(data_set_id=data_set_id)
        except ECommerceIntegration.DoesNotExist:
            return Response({}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(ecommerce_integration, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Delete the ecommerce integration for a data set",
        manual_parameters=[
            openapi.Parameter(
                "data_set_id", openapi.IN_PATH, description="ID of the data set", type=openapi.TYPE_INTEGER
            )
        ],
    )
    def delete(self, *args, **kwargs):
        data_set_id = kwargs["data_set_id"]
        ECommerceIntegration.objects.filter(data_set_id=data_set_id).delete()
        return Response({}, status=status.HTTP_204_NO_CONTENT)


class DataSetECommerceIntegrationSyncView(GenericAPIView):
    permission_classes = [IsAdminUser]

    @swagger_auto_schema(
        operation_description="Sync a document source",
        responses={200: SyncResponseSerializer},
    )
    def post(self, request, *args, **kwargs):
        data_set_id = kwargs["data_set_id"]
        try:
            _ecommerce_integration = ECommerceIntegration.objects.get(data_set_id=data_set_id)
        except ECommerceIntegration.DoesNotExist:
            return Response({}, status=status.HTTP_404_NOT_FOUND)

        task = sync_ecommerce_integrations.apply_async(args=(data_set_id,))
        serializer = SyncResponseSerializer({"task_id": task.id})
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)


class ConfigView(GenericAPIView):
    permission_classes = [IsAdminUser]

    @swagger_auto_schema(
        operation_description="Get catalog configuration",
        responses={
            200: openapi.Response(
                description="Catalog configuration",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "language_model_providers": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_STRING),
                            description="List of available language model providers",
                        ),
                        "embedding_providers": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_STRING),
                            description="List of available embedding providers",
                        ),
                    },
                ),
            )
        },
    )
    def get(self, request, *args, **kwargs):
        response_body = {
            "language_model_providers": settings.CATALOG_LANGUAGE_MODEL_PROVIDERS.keys(),
            "embedding_providers": settings.CATALOG_EMBEDDING_PROVIDERS.keys(),
        }

        return Response(response_body)


class ConfigLanguageModelView(GenericAPIView):
    permission_classes = [IsAdminUser]

    @swagger_auto_schema(
        operation_description="Get available language models for a given provider",
        responses={
            200: openapi.Response(
                description="List of available language models",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(type=openapi.TYPE_STRING),
                ),
            )
        },
    )
    def get(self, request, *args, **kwargs):
        provider_name = kwargs.get("provider_name")
        response_body = LanguageModelRegistry().provider_class_by_name(provider_name).available_models()

        return Response(response_body)


class ConfigEmbeddingModelView(GenericAPIView):
    permission_classes = [IsAdminUser]

    @swagger_auto_schema(
        operation_description="Get available embedding models for a given provider",
        responses={
            200: openapi.Response(
                description="List of available embedding models",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(type=openapi.TYPE_STRING),
                ),
            )
        },
    )
    def get(self, request, *args, **kwargs):
        provider_name = kwargs.get("provider_name")
        response_body = EmbeddingProviderRegistry().provider_class_by_name(provider_name).available_models()

        return Response(response_body)
