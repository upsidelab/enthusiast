from typing import Type

from django.conf import settings
from enthusiast_common.agentic_execution import BaseAgenticExecutionDefinition
from utils.base_registry import BaseRegistry


class AgenticExecutionDefinitionRegistry(BaseRegistry[BaseAgenticExecutionDefinition]):
    plugin_base = BaseAgenticExecutionDefinition

    def get_all(self) -> list[Type[BaseAgenticExecutionDefinition]]:
        return [self._get_plugin_class_by_path(path) for path in settings.AVAILABLE_AGENTIC_EXECUTION_DEFINITIONS]

    def get_by_key(self, key: str) -> Type[BaseAgenticExecutionDefinition]:
        for cls in self.get_all():
            if cls.EXECUTION_KEY == key:
                return cls
        raise KeyError(f"No agentic execution definition registered with EXECUTION_KEY='{key}'.")

    def get_by_agent_type(self, agent_type: str) -> list[Type[BaseAgenticExecutionDefinition]]:
        return [cls for cls in self.get_all() if cls.AGENT_KEY == agent_type]
