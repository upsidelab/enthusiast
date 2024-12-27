from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAdminUser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from account.models import User
from account.serializers import ServiceAccountSerializer, CreateUpdateServiceAccountSerializer

from account.services import ServiceAccountNameService


class CheckServiceNameView(APIView):
    permission_classes = [IsAdminUser]

    @swagger_auto_schema(
        operation_description="Check if a service account name is available",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'name': openapi.Schema(type=openapi.TYPE_STRING, description='Service account name')
            }
        )
    )
    def post(self, request):
        name = request.data.get('name')
        service = ServiceAccountNameService()
        if service.is_service_account_name_available(name):
            return Response({"is_available": True}, status=status.HTTP_200_OK)
        return Response({"is_available": False}, status=status.HTTP_200_OK)


class ResetTokenView(APIView):
    permission_classes = [IsAdminUser]

    @swagger_auto_schema(
        operation_description="Revoke and regenerate a token for a service account",
        manual_parameters=[
            openapi.Parameter('id', openapi.IN_PATH, description='ID of the service account', type=openapi.TYPE_INTEGER)
        ]
    )
    def post(self, request, id):
        service_account = User.objects.get(id=id, is_service_account=True)
        Token.objects.filter(user=service_account).delete()
        token, created = Token.objects.get_or_create(user=service_account)
        return Response({"token": token.key}, status=status.HTTP_200_OK)


class ServiceAccountListView(ListAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = ServiceAccountSerializer
    queryset = User.objects.filter(is_service_account=True).order_by('-date_joined')

    @swagger_auto_schema(
        operation_description="Create a new service account",
        request_body=CreateUpdateServiceAccountSerializer
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
    permission_classes = [IsAdminUser]

    @swagger_auto_schema(
        operation_description="Update a service account",
        request_body=CreateUpdateServiceAccountSerializer,
        manual_parameters=[
            openapi.Parameter('id', openapi.IN_PATH, description='ID of the service account', type=openapi.TYPE_INTEGER)
        ]
    )
    def patch(self, request, id):
        service_account = User.objects.get(id=id, is_service_account=True)
        serializer = CreateUpdateServiceAccountSerializer(service_account, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
