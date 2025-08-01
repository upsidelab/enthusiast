from rest_framework import serializers

from agent.models.configuration import AgentConfiguration
from agent.serializers.customs.fields import PydanticModelField, PydanticModelToolListField
from agent.serializers.customs.serializers import ParentDataContextSerializerMixin
from catalog.models import DataSet


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
    key = serializers.CharField()
    name = serializers.CharField()
    key = serializers.CharField()
    agent_args = serializers.DictField(child=ExtraArgDetailSerializer(), allow_empty=True)
    prompt_inputs = serializers.DictField(child=ExtraArgDetailSerializer(), allow_empty=True)
    prompt_extension = serializers.DictField(child=ExtraArgDetailSerializer(), allow_empty=True)
    tools = serializers.ListField(child=serializers.DictField(child=ExtraArgDetailSerializer()), allow_empty=True)


class AvailableAgentsResponseSerializer(serializers.Serializer):
    choices = serializers.ListField(child=AgentChoiceSerializer())


class AgentConfigSerializer(ParentDataContextSerializerMixin, serializers.Serializer):
    agent_args = PydanticModelField(agent_field_name="AGENT_ARGS")
    prompt_inputs = PydanticModelField(agent_field_name="PROMPT_INPUT_SCHEMA")
    prompt_extension = PydanticModelField(agent_field_name="PROMPT_EXTENSION")
    tools = PydanticModelToolListField(agent_field_name="TOOLS", tool_field_name="CONFIGURATION_ARGS")


class AgentConfigurationSerializer(ParentDataContextSerializerMixin, serializers.ModelSerializer):
    config = AgentConfigSerializer()
    dataset = serializers.PrimaryKeyRelatedField(queryset=DataSet.objects.all())

    class Meta:
        model = AgentConfiguration
        fields = ["id", "name", "config", "dataset", "agent_key", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class AgentConfigurationListSerializer(ParentDataContextSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = AgentConfiguration
        fields = ["id", "name", "dataset", "created_at", "updated_at"]
