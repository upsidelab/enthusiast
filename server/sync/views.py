from django.conf import settings
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from sync.serializers import ProductSourcePluginSerializer


class GetDocumentSourcePlugins(APIView):
    """
    View to check status of an enqueued task that's running in the background.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        response = settings.CATALOG_DOCUMENT_SOURCE_PLUGINS.items()

        return Response(response)


class GetProductSourcePlugins(APIView):
    """
    View to get list of plugins registered in ECL settings.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ProductSourcePluginSerializer
    pagination_class = None

    def get(self, request):
        plugins = settings.CATALOG_PRODUCT_SOURCE_PLUGINS.items()
        data = [{"plugin_name": plugin_name} for plugin_name, plugin_class in plugins]
        serializer = self.serializer_class(data, many=True)

        return Response({"results": serializer.data})
