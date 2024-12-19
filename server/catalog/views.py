from rest_framework import status
from rest_framework.generics import ListAPIView, ListCreateAPIView, GenericAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from account.models import User
from account.serializers import UserSerializer
from .models import DataSet
from .serializers import DataSetSerializer, DocumentSerializer, ProductSerializer


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
