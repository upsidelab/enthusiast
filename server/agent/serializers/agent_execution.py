from pydantic import ValidationError as PydanticValidationError
from rest_framework import serializers

from agent.execution.registry import AgentExecutionRegistry
from agent.models.agent_execution import AgentExecution


class AgentExecutionTypeSerializer(serializers.Serializer):
    """Describes a single available execution type."""

    key = serializers.CharField()
    name = serializers.CharField()
    input_schema = serializers.DictField()


class AgentExecutionSerializer(serializers.ModelSerializer):
    """Read serializer for AgentExecution records."""

    duration_seconds = serializers.FloatField(read_only=True)

    class Meta:
        model = AgentExecution
        fields = [
            "id",
            "execution_type",
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
        read_only_fields = fields


class StartAgentExecutionSerializer(serializers.Serializer):
    """Write serializer for starting a new execution."""

    execution_type = serializers.CharField()
    input = serializers.DictField(default=dict)

    def validate(self, attrs):
        registry = AgentExecutionRegistry()
        try:
            execution_cls = registry.get_by_key(attrs["execution_type"])
        except KeyError:
            raise serializers.ValidationError({"execution_type": f"Unknown execution type '{attrs['execution_type']}'."})

        try:
            validated_input = execution_cls.INPUT_TYPE(**attrs["input"])
        except PydanticValidationError as exc:
            raise serializers.ValidationError(
                {"input": {".".join(str(loc) for loc in e["loc"]): e["msg"] for e in exc.errors()}}
            )
        except Exception as exc:
            raise serializers.ValidationError({"input": str(exc)})

        attrs["input"] = validated_input.model_dump()
        return attrs
