import logging
import urllib.parse

from django.conf import settings
from django.contrib.auth import authenticate
from django.shortcuts import redirect
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from utils.functions import import_from_string

from account.serializers import TokenResponseSerializer

logger = logging.getLogger(__name__)


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


class OTPCallbackView(APIView):
    DEFAULT_ERROR_MESSAGE = "Could not sign in. Please try again."

    @swagger_auto_schema(
        operation_description="Callback endpoint for authentication provider hosted OTP login. Exchanges code for access token and redirects.",
        manual_parameters=[
            openapi.Parameter(
                "code",
                openapi.IN_QUERY,
                description="Authorization code from auth provider",
                type=openapi.TYPE_STRING,
                required=True,
            ),
        ],
        responses={
            200: openapi.Response(description="User authenticated successfully"),
            400: "Bad Request",
            401: "Unauthorized",
        },
    )
    def get(self, request):
        code = request.query_params.get("code")
        redirect_uri = f"{settings.FRONTEND_BASE_URL}/login"
        try:
            otp_service_class = import_from_string(settings.OTP_AUTH_SERVICE)
            otp_service = otp_service_class()
            if not otp_service.is_enabled():
                return redirect(
                    f"{settings.FRONTEND_BASE_URL}/login?{urllib.parse.urlencode({'error': otp_service.NOT_CONFIGURED_ERROR_MESSAGE})}"
                )
            token = otp_service.get_token(code)
            user_email = otp_service.get_email_from_token(token)
            user = otp_service.create_user(email=user_email)
            token = otp_service.create_token(user=user)
            return redirect(f"{redirect_uri}?{urllib.parse.urlencode({'token': token.key})}")
        except Exception as e:
            logger.error(e, exc_info=True)
            return redirect(f"{redirect_uri}?{urllib.parse.urlencode({'error': self.DEFAULT_ERROR_MESSAGE})}")


class OTPStartView(APIView):
    DEFAULT_ERROR_MESSAGE = "Service unavailable, please try again later."

    @swagger_auto_schema(
        operation_description="Start the OTP login flow. Redirects user to the authentication provider hosted login page.",
        responses={
            302: openapi.Response(description="Redirect to authentication provider or frontend login with error"),
            400: "Bad Request",
            503: "Service Unavailable",
        },
    )
    def get(self, request):
        try:
            otp_service_class = import_from_string(settings.OTP_AUTH_SERVICE)
            otp_service = otp_service_class()
            if not otp_service.is_enabled():
                return redirect(
                    f"{settings.FRONTEND_BASE_URL}/login?{urllib.parse.urlencode({'error': otp_service.NOT_CONFIGURED_ERROR_MESSAGE})}"
                )
            auth_url = otp_service.get_redirect_url()

            return redirect(auth_url)

        except Exception as e:
            logger.error(e, exc_info=True)
            return redirect(
                f"{settings.FRONTEND_BASE_URL}/login?{urllib.parse.urlencode({'error': self.DEFAULT_ERROR_MESSAGE})}"
            )
