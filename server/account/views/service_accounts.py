from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from account.models import User
from account.serializers import (
    AvailabilityResponseSerializer,
    CreateUpdateServiceAccountSerializer,
    ServiceAccountSerializer,
    TokenResponseSerializer,
)
from account.services.service_accounts import ServiceAccountNameService
from catalog.utils import ModelPermissions, permission_required_with_global_perms

_user_perms = ModelPermissions(User)


class CheckServiceNameView(APIView):
    permission_classes = [IsAuthenticated]

    @method_decorator(permission_required_with_global_perms(_user_perms.view))
    @swagger_auto_schema(
        operation_description="Check if a service account name is available",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={"name": openapi.Schema(type=openapi.TYPE_STRING, description="Service account name")},
        ),
        responses={200: AvailabilityResponseSerializer},
    )
    def post(self, request):
        name = request.data.get("name")
        service = ServiceAccountNameService()
        is_available = service.is_service_account_name_available(name)
        serializer = AvailabilityResponseSerializer({"is_available": is_available})
        return Response(serializer.data, status=status.HTTP_200_OK)


class ResetTokenView(APIView):
    permission_classes = [IsAuthenticated]

    @method_decorator(permission_required_with_global_perms(_user_perms.change, (User, "pk", "id")))
    @swagger_auto_schema(
        operation_description="Revoke and regenerate a token for a service account",
        manual_parameters=[
            openapi.Parameter("id", openapi.IN_PATH, description="ID of the service account", type=openapi.TYPE_INTEGER)
        ],
        responses={200: TokenResponseSerializer},
    )
    def post(self, request, id):
        service_account = get_object_or_404(User, id=id, is_service_account=True)
        Token.objects.filter(user=service_account).delete()
        token, created = Token.objects.get_or_create(user=service_account)
        serializer = TokenResponseSerializer({"token": token.key})
        return Response(serializer.data, status=status.HTTP_200_OK)


class ServiceAccountListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ServiceAccountSerializer
    queryset = User.objects.filter(is_service_account=True).order_by("-date_joined")

    @method_decorator(permission_required_with_global_perms(_user_perms.view))
    @swagger_auto_schema(
        operation_description="Get list of service accounts",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @method_decorator(permission_required_with_global_perms(_user_perms.add))
    @swagger_auto_schema(
        operation_description="Create a new service account", request_body=CreateUpdateServiceAccountSerializer
    )
    def post(self, request):
        serializer = CreateUpdateServiceAccountSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            response_data = serializer.validated_data
            response_data.update({"id": user.id, "token": token.key})
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ServiceAccountView(APIView):
    permission_classes = [IsAuthenticated]

    @method_decorator(permission_required_with_global_perms(_user_perms.change, (User, "pk", "id")))
    @swagger_auto_schema(
        operation_description="Update a service account",
        request_body=CreateUpdateServiceAccountSerializer,
        manual_parameters=[
            openapi.Parameter("id", openapi.IN_PATH, description="ID of the service account", type=openapi.TYPE_INTEGER)
        ],
    )
    def patch(self, request, id):
        service_account = get_object_or_404(User, id=id, is_service_account=True)
        serializer = CreateUpdateServiceAccountSerializer(service_account, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
