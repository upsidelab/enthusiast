from rest_framework import status
from rest_framework.permissions import IsAdminUser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from account.models import User
from account.serializers import ServiceAccountSerializer, CreateServiceAccountSerializer

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


class RevokeTokenView(APIView):
    permission_classes = [IsAdminUser]

    @swagger_auto_schema(
        operation_description="Revoke and regenerate a token for a service account",
        manual_parameters=[
            openapi.Parameter('id', openapi.IN_PATH, description='ID of the service account', type=openapi.TYPE_INTEGER)
        ]
    )
    def post(self, request, id):
        try:
            service_account = User.objects.get(id=id, is_service_account=True)
            Token.objects.filter(user=service_account).delete()
            token, created = Token.objects.get_or_create(user=service_account)
            return Response({"token": token.key}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "Service account not found"}, status=status.HTTP_404_NOT_FOUND)


class ServiceAccountListView(APIView):
    permission_classes = [IsAdminUser]

    @swagger_auto_schema(
        operation_description="List all active service accounts",
        manual_parameters=[]
    )
    def get(self, request):
        service_accounts = User.objects.filter(is_service_account=True).filter(is_active=True).order_by(
            '-date_joined')
        serializer = ServiceAccountSerializer(service_accounts, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Create a new service account",
        request_body=CreateServiceAccountSerializer
    )
    def post(self, request):
        serializer = CreateServiceAccountSerializer(data=request.data)
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
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'name': openapi.Schema(type=openapi.TYPE_STRING, description='Service account name'),
                'is_active': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Is active')
            },
            required=['name', 'is_active']
        ),
        manual_parameters=[
            openapi.Parameter('id', openapi.IN_PATH, description='ID of the service account', type=openapi.TYPE_INTEGER)
        ]
    )
    def patch(self, request, id):
        try:
            service_account = User.objects.get(id=id, is_service_account=True)
            service = ServiceAccountNameService()
            name = request.data.get('name')
            if name:
                service_account.email = service.generate_service_account_email(name)
            is_active = request.data.get('is_active')
            if is_active is not None:
                service_account.is_active = is_active
            service_account.save()
            serializer = ServiceAccountSerializer(service_account)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "Service account not found"}, status=status.HTTP_404_NOT_FOUND)
