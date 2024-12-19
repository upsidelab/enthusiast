from rest_framework import serializers

class ProductSourcePluginSerializer(serializers.Serializer):
    plugin_name = serializers.CharField()
