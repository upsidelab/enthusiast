from rest_framework import status
from rest_framework.generics import ListAPIView, ListCreateAPIView, GenericAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from account.models import User
from account.serializers import UserSerializer
from .models import DataSet, ProductSource
from .serializers import DataSetSerializer, DocumentSerializer, ProductSerializer, ProductSourceSerializer


class DataSetListView(ListCreateAPIView):
    serializer_class = DataSetSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user and self.request.user.is_staff:
            return DataSet.objects.all()

        return DataSet.objects.filter(users=self.request.user)

    def perform_create(self, serializer):
        if not self.request.user and self.request.user.is_staff:
            self.permission_denied(self.request)

        data_set = serializer.save()
        data_set.users.add(self.request.user)


class DataSetUserListView(ListCreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        return DataSet.objects.get(id=self.kwargs['data_set_id']).users.all()

    def create(self, *args, **kwargs):
        user = User.objects.get(id=self.request.data['user_id'])
        DataSet.objects.get(id=self.kwargs['data_set_id']).users.add(user)
        return Response({}, status=status.HTTP_201_CREATED)


class DataSetUserView(GenericAPIView):
    permission_classes = [IsAdminUser]

    def delete(self, *args, **kwargs):
        DataSet.objects.get(id=self.kwargs['data_set_id']).users.remove(self.kwargs['user_id'])
        return Response({}, status=status.HTTP_204_NO_CONTENT)


class DataSetProductSourceListView(ListCreateAPIView):
    serializer_class = ProductSourceSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        return ProductSource.objects.filter(data_set_id=self.kwargs['data_set_id'])

    def perform_create(self, serializer):
        if not self.request.user and self.request.user.is_staff:
            self.permission_denied(self.request)
        # Get data set from URL (it's not passed via request body).
        data_set_id = self.kwargs.get('data_set_id')
        serializer.save(data_set_id=data_set_id)


class DataSetProductSourceView(GenericAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = ProductSourceSerializer

    def get(self, request, data_set_id, product_source_id):
        product_source = ProductSource.objects.get(id=product_source_id)
        serializer = self.serializer_class(product_source)
        return Response(serializer.data)

    def patch(self, request, *args, **kwargs):
        product_source = ProductSource.objects.get(id=kwargs.get('product_source_id'))
        product_source.plugin_name = request.data.get('plugin_name', product_source.plugin_name)
        product_source.config = request.data.get('config', product_source.config)
        product_source.data_set_id = request.data.get('data_set_id', product_source.data_set_id)
        product_source.save()

        serializer = self.serializer_class(product_source)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, *args, **kwargs):
        ProductSource.objects.filter(id=kwargs['product_source_id']).delete()
        return Response({}, status=status.HTTP_204_NO_CONTENT)


class ProductListView(ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination

    def get_queryset(self):
        if self.request.user.is_staff:
            data_set = DataSet.objects.get(id=self.kwargs['data_set_id'])
        else:
            data_set = DataSet.objects.get(id=self.kwargs['data_set_id'], users=self.request.user)
        return data_set.products.all()


class DocumentListView(ListAPIView):
    serializer_class = DocumentSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination

    def get_queryset(self):
        if self.request.user.is_staff:
            data_set = DataSet.objects.get(id=self.kwargs['data_set_id'])
        else:
            data_set = DataSet.objects.get(id=self.kwargs['data_set_id'], users=self.request.user)
        return data_set.documents.all()
