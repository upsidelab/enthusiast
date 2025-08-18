from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from account.serializers import AccountSerializer


class AccountView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get the current user's account",
        responses={200: AccountSerializer}
    )
    def get(self, request):
        serializer = AccountSerializer(request.user)
        return Response(serializer.data, status=200)
