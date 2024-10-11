from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView


class LoginView(APIView):
    def post(self, request):
        user = authenticate(username=request.data['email'], password=request.data['password'])
        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({"token": token.key})
        return Response({}, status=403)
