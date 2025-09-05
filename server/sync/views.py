from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from sync.document.registry import DocumentSourcePluginRegistry
from sync.product.registry import ProductSourcePluginRegistry
from sync.serializers import AvailablePluginsResponseSerializer
from sync.utils import PluginTypesMixin


class GetDocumentSourcePlugins(APIView, PluginTypesMixin):
    """
    View to get list of plugins registered in ECL settings.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = AvailablePluginsResponseSerializer
    pagination_class = None

    @swagger_auto_schema(
        operation_description="Get list of document source plugins",
        responses={200: AvailablePluginsResponseSerializer(many=True)},
    )
    def get(self, request):
        serializer = self.serializer_class(data=self.get_choices(DocumentSourcePluginRegistry))
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)


class GetProductSourcePlugins(APIView, PluginTypesMixin):
    """
    View to get list of plugins registered in ECL settings.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = AvailablePluginsResponseSerializer
    pagination_class = None

    @swagger_auto_schema(
        operation_description="Get list of product source plugins",
        responses={200: AvailablePluginsResponseSerializer(many=True)},
    )
    def get(self, request):
        serializer = self.serializer_class(data=self.get_choices(ProductSourcePluginRegistry))
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)
