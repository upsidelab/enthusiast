from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from account.models import CustomUser
from account.serializers import CustomUserSerializer


class LoginView(APIView):
    @swagger_auto_schema(
        operation_description="Login to obtain an authentication token",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, description='Email'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='Password')
            }
        ),
        responses={
            200: openapi.Response(
                description="Token retrieved successfully",
                examples={
                    "application/json": {
                        "token": "string"
                    }
                }
            ),
            403: "Forbidden"
        }
    )
    def post(self, request):
        user = authenticate(username=request.data['email'], password=request.data['password'])
        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({"token": token.key})
        return Response({}, status=403)


class AccountView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = CustomUserSerializer(request.user)
        return Response(serializer.data, status=200)


class UserListView(ListAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = CustomUserSerializer

    def get_queryset(self):
        return CustomUser.objects.all()
