from typing import Type

from django.conf import settings
from enthusiast_common.agent_execution import BaseAgentExecution
from utils.base_registry import BaseRegistry


class AgentExecutionRegistry(BaseRegistry[BaseAgentExecution]):
    plugin_base = BaseAgentExecution

    def get_all(self) -> list[Type[BaseAgentExecution]]:
        return [self._get_plugin_class_by_path(path) for path in settings.AVAILABLE_AGENT_EXECUTIONS]

    def get_by_key(self, key: str) -> Type[BaseAgentExecution]:
        for cls in self.get_all():
            if cls.EXECUTION_KEY == key:
                return cls
        raise KeyError(f"No agent execution registered with EXECUTION_KEY='{key}'.")

    def get_by_agent_type(self, agent_type: str) -> list[Type[BaseAgentExecution]]:
        return [cls for cls in self.get_all() if cls.AGENT_KEY == agent_type]
