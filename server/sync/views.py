from django.conf import settings
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from sync.serializers import SourcePluginSerializer


class GetDocumentSourcePlugins(APIView):
    """
    View to get list of plugins registered in ECL settings.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = SourcePluginSerializer
    pagination_class = None

    def get(self, request):
        plugins = settings.CATALOG_DOCUMENT_SOURCE_PLUGINS.items()
        data = [{"plugin_name": plugin_name} for plugin_name, plugin_class in plugins]
        serializer = self.serializer_class(data, many=True)

        return Response({"results": serializer.data})


class GetProductSourcePlugins(APIView):
    """
    View to get list of plugins registered in ECL settings.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = SourcePluginSerializer
    pagination_class = None

    def get(self, request):
        plugins = settings.CATALOG_PRODUCT_SOURCE_PLUGINS.items()
        data = [{"plugin_name": plugin_name} for plugin_name, plugin_class in plugins]
        serializer = self.serializer_class(data, many=True)

        return Response({"results": serializer.data})
