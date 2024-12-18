from rest_framework import status
from rest_framework.permissions import IsAdminUser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

from account.models import CustomUser
from account.serializers import ServiceAccountSerializer, CreateServiceAccountSerializer


class CheckServiceNameView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        name = request.data.get('name')
        email = f"{name}@enthusiast.internal"
        if CustomUser.objects.filter(email=email).exists():
            return Response({"is_available": False}, status=status.HTTP_200_OK)
        return Response({"isAvailable": True}, status=status.HTTP_200_OK)


class RevokeTokenView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, id):
        try:
            service_account = CustomUser.objects.get(id=id, is_service_account=True)
            Token.objects.filter(user=service_account).delete()
            token, created = Token.objects.get_or_create(user=service_account)
            return Response({"token": token.key}, status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response({"error": "Service account not found"}, status=status.HTTP_404_NOT_FOUND)


class ServiceAccountListView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        service_accounts = CustomUser.objects.filter(is_service_account=True).filter(is_active=True).order_by(
            '-date_joined')
        serializer = ServiceAccountSerializer(service_accounts, many=True)
        return Response(serializer.data)

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

    def patch(self, request, id):
        try:
            service_account = CustomUser.objects.get(id=id, is_service_account=True)
            name = request.data.get('name')
            if name:
                service_account.email = f"{name}@enthusiast.internal"
            is_active = request.data.get('is_active')
            if is_active is not None:
                service_account.is_active = is_active
            service_account.save()
            serializer = ServiceAccountSerializer(service_account)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response({"error": "Service account not found"}, status=status.HTTP_404_NOT_FOUND)
