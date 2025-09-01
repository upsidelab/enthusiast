from rest_framework import serializers
from utils.serializers import ExtraArgDetailSerializer


class SourcePluginSerializer(serializers.Serializer):
    plugin_name = serializers.CharField()


class PluginChoiceSerializer(serializers.Serializer):
    name = serializers.CharField()
    configuration_args = serializers.DictField(child=ExtraArgDetailSerializer(), allow_empty=True)


class AvailablePluginsResponseSerializer(serializers.Serializer):
    choices = serializers.ListField(child=PluginChoiceSerializer())
