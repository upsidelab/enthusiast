import inspect
import logging
from abc import ABC, abstractmethod
from importlib import import_module
from typing import Any, Type, TypeVar

from django.conf import settings
from enthusiast_common.agents import BaseAgent
from enthusiast_common.builder import BaseAgentBuilder
from enthusiast_common.config import AgentConfig

from agent.core.agents.default_config import merge_config
from agent.core.builder import AgentBuilder
from agent.models import Conversation

T = TypeVar("T", bound=BaseAgentBuilder)

logger = logging.getLogger(__name__)


class BaseAgentRegistry(ABC):
    def __init__(self, agents_config: dict[Any, Any]):
        self._agents_config = agents_config

    @abstractmethod
    def get_conversation_agent(self, *args, **kwargs) -> BaseAgent:
        pass

    @abstractmethod
    def get_agent_class_by_key(self, *args, **kwargs) -> Type[BaseAgent]:
        pass


class AgentRegistry(BaseAgentRegistry):
    def __init__(self):
        agents_config = settings.AVAILABLE_AGENTS
        super().__init__(agents_config)

    def get_conversation_agent(self, conversation: Conversation, streaming: bool) -> BaseAgent:
        builder = self._get_builder_class_by_name(agent_key=conversation.agent_key)
        config = self._get_config_by_name(
            agent_key=conversation.agent_key, conversation=conversation, streaming=streaming
        )
        config = merge_config(partial=config, conversation_id=conversation.id, streaming=streaming)
        return builder(config).build()

    def get_agent_class_by_key(self, agent_key: str) -> Type[BaseAgent]:
        agent_directory_path = self._get_agent_directory_path(agent_key)
        agent_module_path = f"{agent_directory_path}.agent"
        try:
            agent_module = import_module(agent_module_path)
        except ModuleNotFoundError:
            raise ImportError(f"Cannot import module '{agent_module_path}' for agent '{agent_key}'.")
        agents = [
            obj
            for _, obj in inspect.getmembers(agent_module, inspect.isclass)
            if issubclass(obj, BaseAgent) and obj is not BaseAgent
        ]
        return agents[0] if agents else None

    def _get_agent_directory_path(self, agent_key: str) -> str:
        try:
            agent_settings = self._agents_config[agent_key]
        except KeyError:
            raise ValueError(f"Agent '{agent_key}' is not defined in settings.AVAILABLE_AGENTS.")
        try:
            return agent_settings["agent_directory_path"]
        except KeyError:
            raise ValueError(f"agent_directory_path is not defined for key: '{agent_key}'")

    def _get_config_by_name(self, agent_key: str, conversation: Conversation, streaming: bool) -> AgentConfig:
        agent_directory_path = self._get_agent_directory_path(agent_key)
        config_module_path = f"{agent_directory_path}.config"
        try:
            config_module = import_module(config_module_path)
        except ModuleNotFoundError:
            raise ImportError(f"Cannot import module '{config_module_path}' for agent '{agent_key}'.")

        try:
            get_config = getattr(config_module, "get_config")
        except AttributeError:
            raise ImportError(f"Module '{config_module_path}' has no attribute 'get_config' for agent '{agent_key}'.")

        return get_config(conversation_id=conversation.id, streaming=streaming)

    def _get_builder_class_by_name(self, agent_key: str) -> Type[BaseAgentBuilder]:
        agent_directory_path = self._get_agent_directory_path(agent_key)
        builder_module_path = f"{agent_directory_path}.builder"
        try:
            builder_module = import_module(builder_module_path)
        except ModuleNotFoundError:
            logger.info(
                f"Cannot import module '{builder_module_path}' for agent '{agent_key}'. Defaulting to AgentBuilder."
            )
            return AgentBuilder

        try:
            builder_class = getattr(builder_module, "Builder")
        except AttributeError:
            raise ImportError(f"Module '{builder_module_path}' has no attribute 'Builder' for agent '{agent_key}'.")

        return builder_class
