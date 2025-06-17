from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import ListCreateAPIView, UpdateAPIView
from rest_framework.permissions import IsAdminUser

from account.models import User
from account.serializers import UserSerializer, UserUpdatePasswordSerializer, UserUpdateSerializer


class UserListView(ListCreateAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = UserSerializer

    @swagger_auto_schema(operation_description="List all users", manual_parameters=[])
    def get_queryset(self):
        return User.objects.filter(is_service_account=False)

    @swagger_auto_schema(operation_description="Create a new user", request_body=UserSerializer)
    def perform_create(self, serializer):
        User.objects.create_user(
            email=serializer.validated_data["email"],
            password=serializer.validated_data["password"],
            is_active=serializer.validated_data["is_active"],
            is_staff=serializer.validated_data["is_staff"],
        )


class UserView(UpdateAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = UserUpdateSerializer

    @swagger_auto_schema(
        operation_description="Update a user",
        request_body=UserUpdateSerializer,
        manual_parameters=[
            openapi.Parameter("id", openapi.IN_PATH, description="ID of the user", type=openapi.TYPE_INTEGER)
        ],
    )
    def get_object(self):
        return User.objects.get(id=self.kwargs["id"], is_service_account=False)

    def perform_update(self, serializer):
        user = self.get_object()
        user.email = serializer.validated_data["email"]
        user.is_active = serializer.validated_data["is_active"]
        user.is_staff = serializer.validated_data["is_staff"]
        user.save()


class UserPasswordView(UpdateAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = UserUpdatePasswordSerializer

    @swagger_auto_schema(
        operation_description="Update a user's password",
        request_body=UserUpdatePasswordSerializer,
        manual_parameters=[
            openapi.Parameter("id", openapi.IN_PATH, description="ID of the user", type=openapi.TYPE_INTEGER)
        ],
    )
    def get_object(self):
        return User.objects.get(id=self.kwargs["id"], is_service_account=False)

    def perform_update(self, serializer):
        user = self.get_object()
        user.set_password(serializer.validated_data["password"])
        user.save()
