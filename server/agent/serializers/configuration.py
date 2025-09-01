from rest_framework import serializers
from utils.serializers import ExtraArgDetailSerializer, ParentDataContextSerializerMixin

from agent.models import Agent
from agent.serializers.customs.fields import PydanticModelField, PydanticModelToolListField
from catalog.models import DataSet


class AgentChoiceSerializer(serializers.Serializer):
    key = serializers.CharField()
    name = serializers.CharField()
    agent_args = serializers.DictField(child=ExtraArgDetailSerializer(), allow_empty=True)
    prompt_input = serializers.DictField(child=ExtraArgDetailSerializer(), allow_empty=True)
    prompt_extension = serializers.DictField(child=ExtraArgDetailSerializer(), allow_empty=True)
    tools = serializers.ListField(child=serializers.DictField(child=ExtraArgDetailSerializer()), allow_empty=True)


class AvailableAgentsResponseSerializer(serializers.Serializer):
    choices = serializers.ListField(child=AgentChoiceSerializer())


class AgentConfigSerializer(ParentDataContextSerializerMixin, serializers.Serializer):
    context_keys_to_propagate = ["agent_type"]

    agent_args = PydanticModelField(agent_field_name="AGENT_ARGS")
    prompt_input = PydanticModelField(agent_field_name="PROMPT_INPUT")
    prompt_extension = PydanticModelField(agent_field_name="PROMPT_EXTENSION")
    tools = PydanticModelToolListField(agent_field_name="TOOLS", tool_field_name="CONFIGURATION_ARGS")


class AgentSerializer(ParentDataContextSerializerMixin, serializers.ModelSerializer):
    context_keys_to_propagate = ["agent_type"]

    config = AgentConfigSerializer()
    dataset = serializers.PrimaryKeyRelatedField(queryset=DataSet.objects.all())

    class Meta:
        model = Agent
        fields = ["id", "name", "description", "config", "dataset", "agent_type", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class AgentListSerializer(ParentDataContextSerializerMixin, serializers.ModelSerializer):
    context_keys_to_propagate = ["agent_type"]

    class Meta:
        model = Agent
        fields = ["id", "name", "dataset", "agent_type", "created_at", "updated_at", "deleted_at", "corrupted"]
