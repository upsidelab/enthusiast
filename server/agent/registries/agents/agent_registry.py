from abc import ABC, abstractmethod
from importlib import import_module
from typing import Any, Type, TypeVar

from django.conf import settings
from enthusiast_common.agents import BaseAgent
from enthusiast_common.builder import BaseAgentBuilder
from enthusiast_common.config import AgentConfig

from agent.core.agents.default_config import merge_config
from agent.models import Conversation

T = TypeVar("T", bound=BaseAgentBuilder)


class BaseAgentRegistry(ABC):
    def __init__(self, agents_config: dict[Any, Any]):
        self._agents_config = agents_config

    @abstractmethod
    def get_agent_by_name(self, *args, **kwargs) -> BaseAgent:
        pass


class AgentRegistry(BaseAgentRegistry):
    def __init__(self):
        agents_config = settings.AVAILABLE_AGENTS
        super().__init__(agents_config)

    def get_agent_by_name(self, conversation: Conversation, streaming: bool) -> BaseAgent:
        builder = self._get_builder_class_by_name(conversation.agent)
        config = self._get_config_by_name(name=conversation.agent, conversation=conversation, streaming=streaming)
        config = merge_config(partial=config)
        return builder(config).build()

    def _get_agent_directory_path(self, name: str) -> str:
        try:
            return self._agents_config[name]
        except KeyError:
            raise ValueError(f"Agent '{name}' is not defined in settings.AVAILABLE_AGENTS.")

    def _get_config_by_name(self, name: str, conversation: Conversation, streaming: bool) -> AgentConfig:
        agent_directory_path = self._get_agent_directory_path(name)
        config_module_path = f"{agent_directory_path}.config"
        try:
            config_module = import_module(config_module_path)
        except ModuleNotFoundError:
            raise ImportError(f"Cannot import module '{config_module_path}' for agent '{name}'.")

        try:
            get_config = getattr(config_module, "get_config")
        except AttributeError:
            raise ImportError(f"Module '{config_module_path}' has no attribute 'get_config' for agent '{name}'.")

        return get_config(conversation_id=conversation.id, streaming=streaming)

    def _get_builder_class_by_name(self, name) -> Type[BaseAgentBuilder]:
        agent_directory_path = self._get_agent_directory_path(name)
        builder_module_path = f"{agent_directory_path}.builder"
        try:
            builder_module = import_module(builder_module_path)
        except ModuleNotFoundError:
            raise ImportError(f"Cannot import module '{builder_module_path}' for agent '{name}'.")

        try:
            builder_class = getattr(builder_module, "Builder")
        except AttributeError:
            raise ImportError(f"Module '{builder_module_path}' has no attribute 'Builder' for agent '{name}'.")

        return builder_class
