from rest_framework import serializers


class ParentDataContextSerializerMixin:
    context_keys_to_propagate = ["agent_key"]

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
