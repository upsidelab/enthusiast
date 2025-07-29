from rest_framework import serializers


class TypeInfoSerializer(serializers.Serializer):
    container = serializers.CharField(
        required=False, allow_null=True, help_text="e.g. 'list', 'dict', or null for flat types"
    )
    inner_type = serializers.CharField(required=False, allow_blank=True, help_text="e.g. 'str', 'int', etc.")
    key_type = serializers.CharField(required=False, allow_blank=True, help_text="For dicts only")
    value_type = serializers.CharField(required=False, allow_blank=True, help_text="For dicts only")
    nullable = serializers.BooleanField(required=False, help_text="True if field is Optional")


class ExtraArgDetailSerializer(serializers.Serializer):
    type = TypeInfoSerializer()
    description = serializers.CharField(allow_blank=True, required=False, allow_null=True)
    title = serializers.CharField(allow_blank=True, required=False, allow_null=True)


class AgentChoiceSerializer(serializers.Serializer):
    name = serializers.CharField()
    key = serializers.CharField()
    agent_args = serializers.DictField(child=ExtraArgDetailSerializer(), allow_empty=True)
    prompt_inputs = serializers.DictField(child=ExtraArgDetailSerializer(), allow_empty=True)
    prompt_extension = serializers.DictField(child=ExtraArgDetailSerializer(), allow_empty=True)
    tools = serializers.ListField(child=serializers.DictField(child=ExtraArgDetailSerializer()), allow_empty=True)


class AvailableAgentsResponseSerializer(serializers.Serializer):
    choices = serializers.ListField(child=AgentChoiceSerializer())
