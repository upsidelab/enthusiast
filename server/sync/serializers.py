from rest_framework import serializers


class SourcePluginSerializer(serializers.Serializer):
    plugin_name = serializers.CharField()


class PluginChoiceSerializer(serializers.Serializer):
    name = serializers.CharField()
    configuration_args = serializers.DictField(allow_empty=True)


class AvailablePluginsResponseSerializer(serializers.Serializer):
    choices = serializers.ListField(child=PluginChoiceSerializer())
