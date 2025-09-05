from pydantic import ValidationError as PydanticValidationError
from rest_framework import serializers


class ParentDataContextSerializerMixin:
    context_keys_to_propagate = []

    def to_internal_value(self, data):
        for key in self.context_keys_to_propagate:
            if key in data and key not in self.context:
                self.context[key] = data[key]

        self._propagate_context(data)
        return super().to_internal_value(data)

    def _propagate_context(self, data):
        for field_name, field in self.fields.items():
            if isinstance(field, serializers.BaseSerializer):
                for key in self.context_keys_to_propagate:
                    if key in self.context:
                        field.context[key] = self.context[key]

            elif hasattr(field, "child") and isinstance(field.child, serializers.BaseSerializer):
                for key in self.context_keys_to_propagate:
                    if key in self.context:
                        field.child.context[key] = self.context[key]


class BasePydanticModelField(serializers.Field):
    def _format_pydantic_errors(self, e: PydanticValidationError):
        error_dict = {}
        for err in e.errors():
            field_path = ".".join(str(x) for x in err["loc"])
            error_dict.setdefault(field_path, []).append(err["msg"])
        return error_dict


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
