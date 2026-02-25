from typing import Type

from utils.functions import get_model_descriptor_from_class_field

from sync.base import SourcePluginRegistry


class PluginTypesMixin:
    def get_choices(self, plugin_registry_class: Type[SourcePluginRegistry]):
        plugin_registry = plugin_registry_class()
        choices = []
        for plugin_class in plugin_registry.get_plugin_classes():
            choices.append(
                {
                    "name": plugin_class.NAME,
                    "configuration_args": get_model_descriptor_from_class_field(plugin_class, "CONFIGURATION_ARGS"),
                }
            )
        return {"choices": choices}
