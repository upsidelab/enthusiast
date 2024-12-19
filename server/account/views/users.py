from rest_framework.generics import ListCreateAPIView, UpdateAPIView
from rest_framework.permissions import IsAdminUser

from account.models import User
from account.serializers import UserSerializer, UserUpdateSerializer, UserUpdatePasswordSerializer


class UserListView(ListCreateAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = UserSerializer

    def get_queryset(self):
        return User.objects.all()

    def perform_create(self, serializer):
        User.objects.create_user(
            email=serializer.validated_data['email'],
            password=serializer.validated_data['password'],
            is_active=serializer.validated_data['is_active'],
            is_staff=serializer.validated_data['is_staff']
        )


class UserView(UpdateAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = UserUpdateSerializer

    def get_object(self):
        return User.objects.get(id=self.kwargs['id'])

    def perform_update(self, serializer):
        user = self.get_object()
        user.email = serializer.validated_data['email']
        user.is_active = serializer.validated_data['is_active']
        user.is_staff = serializer.validated_data['is_staff']
        user.save()


class UserPasswordView(UpdateAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = UserUpdatePasswordSerializer

    def get_object(self):
        return User.objects.get(id=self.kwargs['id'])

    def perform_update(self, serializer):
        user = self.get_object()
        user.set_password(serializer.validated_data['password'])
        user.save()
