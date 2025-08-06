from drf_yasg import openapi
from pydantic import BaseModel
from pydantic import ValidationError as PydanticValidationError
from rest_framework import serializers
from rest_framework.exceptions import APIException

from agent.registries.agents.agent_registry import AgentRegistry


class BasePydanticModelField(serializers.Field):
    def _format_pydantic_errors(self, e: PydanticValidationError):
        error_dict = {}
        for err in e.errors():
            field_path = ".".join(str(x) for x in err["loc"])
            error_dict.setdefault(field_path, []).append(err["msg"])
        return error_dict


class PydanticModelField(BasePydanticModelField):
    def __init__(self, *, agent_field_name: str, **kwargs):
        self.agent_field_name = agent_field_name
        super().__init__(**kwargs)

    def to_internal_value(self, data):
        agent_key = self.context.get("agent_key")
        if not agent_key:
            raise AssertionError("Missing 'agent_key' in field context")

        try:
            class_obj = AgentRegistry().get_agent_class_by_key(agent_key)
        except Exception as e:
            raise APIException(f"Error loading agent: {str(e)}")

        try:
            schema = getattr(class_obj, self.agent_field_name)
        except KeyError:
            raise serializers.ValidationError(f"Unknown schema for field: {self.agent_field_name}")

        if not schema:
            return {}

        try:
            return schema(**data).model_dump()
        except PydanticValidationError as e:
            raise serializers.ValidationError(self._format_pydantic_errors(e))

    def to_representation(self, value):
        if isinstance(value, BaseModel):
            return value.model_dump()
        return value

    def get_schema(self, **kwargs):
        return openapi.Schema(type=openapi.TYPE_OBJECT)


class PydanticModelToolListField(BasePydanticModelField):
    def __init__(self, *, agent_field_name: str, tool_field_name: str, **kwargs):
        self.agent_field_name = agent_field_name
        self.tool_field_name = tool_field_name
        super().__init__(**kwargs)

    def to_internal_value(self, data):
        agent_key = self.context.get("agent_key")
        if not agent_key:
            raise AssertionError("Missing 'agent_key' in field context")

        try:
            class_obj = AgentRegistry().get_agent_class_by_key(agent_key)
            tool_list = getattr(class_obj, self.agent_field_name)
        except Exception as e:
            raise serializers.ValidationError(f"Error loading agent or field: {str(e)}")

        if not isinstance(data, list):
            raise serializers.ValidationError("Expected a list of tool configurations.")
        if len(tool_list) != len(data):
            raise serializers.ValidationError("Mismatch between number of tools and provided configs.")

        validated = []
        all_errors = []
        has_errors = False

        for idx, (tool_class, tool_config) in enumerate(zip(tool_list, data)):
            config_schema = getattr(tool_class, self.tool_field_name, None)
            if not config_schema or not isinstance(config_schema, type) or not issubclass(config_schema, BaseModel):
                all_errors.append({})
                validated.append({})
                continue

            try:
                instance = config_schema(**tool_config)
                validated.append(instance.model_dump())
                all_errors.append({})
            except PydanticValidationError as e:
                has_errors = True
                all_errors.append(self._format_pydantic_errors(e))
                validated.append(None)

        if has_errors:
            raise serializers.ValidationError(all_errors)

        return validated

    def to_representation(self, value):
        if isinstance(value, list) and all(isinstance(v, BaseModel) for v in value):
            return [v.model_dump() for v in value]
        return value

    def get_schema(self, **kwargs):
        return openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_OBJECT))
