from typing import Type

from drf_yasg import openapi
from pydantic import BaseModel
from pydantic import ValidationError as PydanticValidationError
from rest_framework import serializers
from rest_framework.exceptions import APIException
from utils.serializers import BasePydanticModelField

from sync.base import SourcePluginRegistry


class PydanticModelField(BasePydanticModelField):
    def __init__(self, *, config_field_name: str, plugin_registry_class: Type[SourcePluginRegistry], **kwargs):
        self.config_field_name = config_field_name
        self.plugin_registry_class = plugin_registry_class
        super().__init__(**kwargs)

    def to_internal_value(self, data):
        plugin_name = self.context.get("plugin_name")
        try:
            class_obj = self.plugin_registry_class().get_plugin_class_by_name(plugin_name)
        except Exception as e:
            raise APIException(f"Error loading plugin: {str(e)}")

        try:
            schema = getattr(class_obj, self.config_field_name)
        except KeyError:
            raise serializers.ValidationError(f"Unknown schema for field: {self.config_field_name}")

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
