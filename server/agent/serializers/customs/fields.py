from drf_yasg import openapi
from pydantic import BaseModel
from pydantic import ValidationError as PydanticValidationError
from rest_framework import serializers
from rest_framework.exceptions import APIException
from utils.serializers import BasePydanticModelField

from agent.core.registries.agents.agent_registry import AgentRegistry


class PydanticModelField(BasePydanticModelField):
    def __init__(self, *, agent_field_name: str, **kwargs):
        self.agent_field_name = agent_field_name
        super().__init__(**kwargs)

    def to_internal_value(self, data):
        agent_type = self.context.get("agent_type")
        if not agent_type:
            raise AssertionError("Missing 'agent_type' in field context")

        try:
            class_obj = AgentRegistry().get_agent_class_by_type(agent_type)
        except Exception as e:
            raise APIException(f"Error loading agent: {str(e)}")

        try:
            schema = getattr(class_obj, self.agent_field_name)
        except AttributeError:
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

    class Meta:
        swagger_schema_fields = {"type": openapi.TYPE_OBJECT}


class PydanticModelToolConfigField(BasePydanticModelField):
    def __init__(self, *, agent_field_name: str, tool_field_name: str, **kwargs):
        self.agent_field_name = agent_field_name
        self.tool_field_name = tool_field_name
        super().__init__(**kwargs)

    def to_internal_value(self, data):
        agent_type = self.context.get("agent_type")
        if not agent_type:
            raise AssertionError("Missing 'agent_type' in field context")

        try:
            class_obj = AgentRegistry().get_agent_class_by_type(agent_type)
            tool_config_list = getattr(class_obj, self.agent_field_name)
        except Exception as e:
            raise serializers.ValidationError(f"Error loading agent or field: {str(e)}")

        if not isinstance(data, dict):
            raise serializers.ValidationError("Expected a dict of tool configurations keyed by tool name.")

        tool_map = {
            tc.tool_class.NAME: tc
            for tc in tool_config_list
            if getattr(tc.tool_class, "NAME", None) is not None
        }

        validated = {}
        all_errors = {}
        has_errors = False

        for tc in tool_config_list:
            config_schema = getattr(tc, self.tool_field_name, None)
            if not config_schema or not isinstance(config_schema, type) or not issubclass(config_schema, BaseModel):
                continue
            tool_name = getattr(tc.tool_class, "NAME", None)
            if tool_name is not None and tool_name not in data:
                all_errors[tool_name] = [f"Configuration required for tool: {tool_name}"]
                has_errors = True

        for tool_name, tool_config_dict in data.items():
            tc = tool_map.get(tool_name)
            if tc is None:
                all_errors[tool_name] = [f"Unknown tool: {tool_name}"]
                has_errors = True
                continue

            config_schema = getattr(tc, self.tool_field_name, None)
            if not config_schema or not isinstance(config_schema, type) or not issubclass(config_schema, BaseModel):
                validated[tool_name] = {}
                continue

            if not isinstance(tool_config_dict, dict):
                all_errors[tool_name] = ["Expected a dict of field values."]
                has_errors = True
                continue

            try:
                instance = config_schema(**tool_config_dict)
                validated[tool_name] = instance.model_dump()
            except PydanticValidationError as e:
                has_errors = True
                all_errors[tool_name] = self._format_pydantic_errors(e)

        if has_errors:
            raise serializers.ValidationError(all_errors)

        return validated

    def to_representation(self, value):
        return value

    class Meta:
        swagger_schema_fields = {"type": openapi.TYPE_OBJECT}
