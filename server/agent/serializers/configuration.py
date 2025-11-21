from enthusiast_common.agents import AgentType
from rest_framework import serializers
from rest_framework.exceptions import APIException
from utils.serializers import ExtraArgDetailSerializer, ParentDataContextSerializerMixin

from agent.core.registries.agents.agent_registry import AgentRegistry
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
    type = serializers.ChoiceField(choices=[type.value for type in AgentType])


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
        fields = [
            "id",
            "name",
            "description",
            "config",
            "dataset",
            "agent_type",
            "created_at",
            "updated_at",
            "file_upload",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "file_upload"]

    def create(self, validated_data):
        agent_type = self.context.get("agent_type")
        if not agent_type:
            raise AssertionError("Missing 'agent_type' in field context")

        try:
            class_obj = AgentRegistry().get_agent_class_by_type(agent_type)
        except Exception as e:
            raise APIException(f"Error loading agent: {str(e)}")
        validated_data["file_upload"] = class_obj.FILE_UPLOAD
        return super().create(validated_data)

    def update(self, instance, validated_data):
        agent_type = self.context.get("agent_type")
        if not agent_type:
            raise AssertionError("Missing 'agent_type' in field context")

        try:
            class_obj = AgentRegistry().get_agent_class_by_type(agent_type)
        except Exception as e:
            raise APIException(f"Error loading agent: {str(e)}")

        validated_data["file_upload"] = class_obj.FILE_UPLOAD
        return super().update(instance, validated_data)


class AgentListSerializer(ParentDataContextSerializerMixin, serializers.ModelSerializer):
    context_keys_to_propagate = ["agent_type"]

    class Meta:
        model = Agent
        fields = ["id", "name", "dataset", "agent_type", "created_at", "updated_at", "deleted_at", "corrupted"]
