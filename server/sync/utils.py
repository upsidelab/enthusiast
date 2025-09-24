from typing import Type

from utils.functions import get_model_descriptor_from_class_field

from sync.base import SourcePluginRegistry


class PluginTypesMixin:
    def get_choices(self, plugin_registry_class: Type[SourcePluginRegistry]):
        plugin_registry = plugin_registry_class()
        choices = []
        for key, _ in plugin_registry.get_plugins():
            choices.append(
                {
                    "name": key,
                    "configuration_args": get_model_descriptor_from_class_field(
                        plugin_registry.get_plugin_class_by_name(key), "CONFIGURATION_ARGS"
                    ),
                }
            )
        return {"choices": choices}
