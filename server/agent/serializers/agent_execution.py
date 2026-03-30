import json

from pydantic import ValidationError as PydanticValidationError
from rest_framework import serializers

from agent.models.agent_execution import AgentExecution
from agent.serializers.conversation import ConversationFileSerializer

_BASE_FIELDS = [
    "id",
    "agent",
    "execution_key",
    "conversation",
    "status",
    "input",
    "result",
    "failure_code",
    "failure_explanation",
    "celery_task_id",
    "started_at",
    "finished_at",
    "duration_seconds",
]


class AgentExecutionSerializer(serializers.ModelSerializer):
    """Lightweight read serializer used for list responses."""

    duration_seconds = serializers.FloatField(read_only=True)

    class Meta:
        model = AgentExecution
        fields = _BASE_FIELDS
        read_only_fields = _BASE_FIELDS


class AgentExecutionDetailSerializer(AgentExecutionSerializer):
    """Extended read serializer used for the detail endpoint. Includes uploaded files."""

    files = serializers.SerializerMethodField()

    class Meta(AgentExecutionSerializer.Meta):
        fields = _BASE_FIELDS + ["files"]
        read_only_fields = fields

    def get_files(self, obj: AgentExecution):
        """Return non-hidden files attached to the execution's conversation."""
        return ConversationFileSerializer(obj.conversation.files.filter(is_hidden=False), many=True).data


class AgentExecutionTypeSerializer(serializers.Serializer):
    """Read serializer for an available execution type on an agent."""

    key = serializers.CharField()
    name = serializers.CharField()
    description = serializers.CharField(allow_null=True)
    input_schema = serializers.DictField()


class StartAgentExecutionSerializer(serializers.Serializer):
    """Write serializer for starting a new execution.

    The agent is resolved from the URL; this serializer validates the
    ``execution_key`` and the input payload against the matching ExecutionInputType.
    Pass the resolved execution class as ``context["execution_cls"]``.
    """

    execution_key = serializers.CharField()
    input = serializers.DictField(default=dict)

    def to_internal_value(self, data):
        # When the request is multipart/form-data, `input` arrives as a JSON-encoded string.
        # QueryDict must be collapsed to a plain dict so that DictField.get_value uses the
        # normal dict path rather than the HTML form-parsing path.
        if isinstance(data.get("input"), str):
            try:
                plain_data = data.dict() if hasattr(data, "dict") else dict(data)
                plain_data["input"] = json.loads(plain_data["input"])
                data = plain_data
            except json.JSONDecodeError as exc:
                raise serializers.ValidationError({"input": f"Invalid JSON: {exc}"})
        return super().to_internal_value(data)

    def validate_input(self, value):
        execution_cls = self.context["execution_cls"]
        try:
            validated = execution_cls.INPUT_TYPE(**value)
        except PydanticValidationError as exc:
            raise serializers.ValidationError(
                {".".join(str(loc) for loc in e["loc"]): e["msg"] for e in exc.errors()}
            )
        except Exception as exc:
            raise serializers.ValidationError(str(exc))
        return validated.model_dump()
