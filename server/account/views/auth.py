import logging
import urllib
from typing import Type

from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.middleware.csrf import get_token
from django.shortcuts import redirect
from django.views import View
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from rest_framework.views import APIView
from utils.functions import import_from_string

from account.services.sso_provider import SSOProviderService

logger = logging.getLogger(__name__)


class LoginView(APIView):
    @swagger_auto_schema(
        operation_description="Log in with session cookie.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "email": openapi.Schema(type=openapi.TYPE_STRING, description="Email"),
                "password": openapi.Schema(type=openapi.TYPE_STRING, description="Password"),
            },
        ),
        responses={200: "OK", 403: "Forbidden"},
    )
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        if not email or not password:
            return Response({}, status=400)
        user = authenticate(username=email, password=password)
        if user:
            login(request, user)
            return Response({})
        return Response({}, status=403)


class LogoutView(APIView):
    @swagger_auto_schema(operation_description="Log out (clear session)", responses={200: "OK"})
    def post(self, request):
        logout(request)
        return Response({})


class CSRFView(View):
    def get(self, request):
        get_token(request)
        return JsonResponse({"csrfToken": get_token(request)})


class SSOProviderLoginView(View):
    DEFAULT_ERROR_MESSAGE = "Service unavailable, please try again later."

    def get(self, request: HttpRequest) -> HttpResponse:
        try:
            sso_provider_service: Type[SSOProviderService] = import_from_string(settings.SSO_PROVIDER_SERVICE)
            if not sso_provider_service.is_enabled():
                return redirect(
                    f"{settings.FRONTEND_BASE_URL}/login?{urllib.parse.urlencode({'error': sso_provider_service.NOT_CONFIGURED_ERROR_MESSAGE})}"
                )
            return SSOProviderService.login()
        except Exception as e:
            logger.error(e, exc_info=True)
            return redirect(
                f"{settings.FRONTEND_BASE_URL}/login?{urllib.parse.urlencode({'error': self.DEFAULT_ERROR_MESSAGE})}"
            )
