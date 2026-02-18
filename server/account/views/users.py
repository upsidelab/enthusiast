from django.utils.decorators import method_decorator
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import ListCreateAPIView, UpdateAPIView, get_object_or_404
from rest_framework.permissions import IsAuthenticated

from account.models import User
from account.serializers import UserSerializer, UserUpdatePasswordSerializer, UserUpdateSerializer
from account.services import UserService
from catalog.utils import ModelPermissions, permission_required_with_global_perms

_user_perms = ModelPermissions(User)


class UserListView(ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    @method_decorator(permission_required_with_global_perms(_user_perms.view))
    @swagger_auto_schema(operation_description="List all users", manual_parameters=[])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return User.objects.filter(is_service_account=False)

    @method_decorator(permission_required_with_global_perms(_user_perms.add))
    @swagger_auto_schema(operation_description="Create a new user", request_body=UserSerializer)
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def perform_create(self, serializer):
        UserService.create_user(
            email=serializer.validated_data["email"],
            password=serializer.validated_data["password"],
            is_active=serializer.validated_data["is_active"],
            is_staff=serializer.validated_data["is_staff"],
        )


class UserView(UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserUpdateSerializer

    @swagger_auto_schema(
        operation_description="Update a user",
        request_body=UserUpdateSerializer,
        manual_parameters=[
            openapi.Parameter("id", openapi.IN_PATH, description="ID of the user", type=openapi.TYPE_INTEGER)
        ],
    )
    def get_object(self):
        return get_object_or_404(User, id=self.kwargs["id"], is_service_account=False)

    @method_decorator(permission_required_with_global_perms(_user_perms.change, (User, "pk", "id")))
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    def perform_update(self, serializer):
        user = self.get_object()
        user.email = serializer.validated_data["email"]
        user.is_active = serializer.validated_data["is_active"]
        user.is_staff = serializer.validated_data["is_staff"]
        user.save()


class UserPasswordView(UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserUpdatePasswordSerializer

    @swagger_auto_schema(
        operation_description="Update a user's password",
        request_body=UserUpdatePasswordSerializer,
        manual_parameters=[
            openapi.Parameter("id", openapi.IN_PATH, description="ID of the user", type=openapi.TYPE_INTEGER)
        ],
    )
    def get_object(self):
        return get_object_or_404(User, id=self.kwargs["id"], is_service_account=False)

    @method_decorator(permission_required_with_global_perms(_user_perms.change, (User, "pk", "id")))
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    def perform_update(self, serializer):
        user = self.get_object()
        user.set_password(serializer.validated_data["password"])
        user.save()
