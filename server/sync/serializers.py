from rest_framework import serializers


class SourcePluginSerializer(serializers.Serializer):
    plugin_name = serializers.CharField()
