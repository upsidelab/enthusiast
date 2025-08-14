from django.contrib.auth import authenticate
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView

from account.serializers import TokenResponseSerializer


class LoginView(APIView):
    @swagger_auto_schema(
        operation_description="Login to obtain an authentication token",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "email": openapi.Schema(type=openapi.TYPE_STRING, description="Email"),
                "password": openapi.Schema(type=openapi.TYPE_STRING, description="Password"),
            },
        ),
        responses={
            200: TokenResponseSerializer,
            403: "Forbidden",
        },
    )
    def post(self, request):
        user = authenticate(username=request.data["email"], password=request.data["password"])
        if user:
            token, created = Token.objects.get_or_create(user=user)
            serializer = TokenResponseSerializer({"token": token.key})
            return Response(serializer.data)
        return Response({}, status=403)
