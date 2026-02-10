import logging
from abc import ABC, abstractmethod
from importlib import import_module
from typing import List, Type

from django.conf import settings
from enthusiast_common.agents import BaseAgent
from enthusiast_common.builder import BaseAgentBuilder
from enthusiast_common.config import AgentConfig
from utils.base_registry import BaseRegistry

from agent.core.agents.default_config import merge_config
from agent.core.builder import AgentBuilder
from agent.models import Conversation

logger = logging.getLogger(__name__)


class AgentRegistryError(Exception):
    """Base exception for all AgentRegistry errors."""


class AgentNotFoundError(AgentRegistryError):
    """Raised when agent type is not found in config."""


class AgentConfigError(AgentRegistryError):
    """Raised when agent configuration is missing or invalid."""


class AgentImportError(AgentRegistryError):
    """Raised when an agent module or class cannot be imported."""


class BaseAgentRegistry(ABC, BaseRegistry[BaseAgent]):
    plugin_base = BaseAgent

    @abstractmethod
    def get_conversation_agent(self, *args, **kwargs) -> BaseAgent:
        pass

    @abstractmethod
    def get_agent_class_by_type(self, *args, **kwargs) -> Type[BaseAgent]:
        pass


class AgentRegistry(BaseAgentRegistry):

    def get_conversation_agent(self, conversation: Conversation, streaming: bool) -> BaseAgent:
        try:
            builder = self._get_builder_class_by_name(agent_type=conversation.agent.agent_type)
            config = self._get_config_by_name(agent_type=conversation.agent.agent_type)
            config = merge_config(partial=config)
            return builder(config=config, conversation_id=conversation.id, streaming=streaming).build()
        except Exception as e:
            raise AgentRegistryError(f"Failed to build agent for conversation {conversation.id}") from e

    def get_agent_class_by_type(self, agent_type: str) -> Type[BaseAgent]:
        agents = [agent for agent in self.get_plugin_classes() if agent.AGENT_KEY == agent_type]

        if not agents:
            raise AgentNotFoundError(f"Could not find agent type '{agent_type}'.")

        return agents[0]

    def get_plugin_classes(self) -> List[Type[BaseAgent]]:
        return [self._get_plugin_class_by_path(path) for path in self._get_plugin_paths()]

    @staticmethod
    def _get_plugin_paths() -> List[str]:
        return settings.AVAILABLE_AGENTS

    def _get_plugin_directory_paths_by_types(self) -> dict[str, str]:
        return {
            self._get_plugin_class_by_path(path).AGENT_KEY: path.rsplit(".", 1)[0]
            for path in self._get_plugin_paths()
        }

    def _get_agent_directory_path(self, agent_type: str) -> str:
        try:
            return self._get_plugin_directory_paths_by_types()[agent_type]
        except KeyError as e:
            raise AgentNotFoundError(f"Agent with AGENT_KEY: '{agent_type}' is not defined in settings.AVAILABLE_AGENTS.") from e

    def _get_config_by_name(self, agent_type: str) -> AgentConfig:
        agent_directory_path = self._get_agent_directory_path(agent_type)
        config_module_path = f"{agent_directory_path}.config"
        try:
            config_module = import_module(config_module_path)
        except ModuleNotFoundError as e:
            raise AgentImportError(f"Cannot import module '{config_module_path}' for agent '{agent_type}'.") from e

        try:
            get_config = getattr(config_module, "get_config")
        except AttributeError as e:
            raise AgentImportError(f"Module '{config_module_path}' has no attribute 'get_config'.") from e

        return get_config()

    def _get_builder_class_by_name(self, agent_type: str) -> Type[BaseAgentBuilder]:
        agent_directory_path = self._get_agent_directory_path(agent_type)
        try:
            return self._get_class_by_path(agent_directory_path, BaseAgentBuilder)
        except (ModuleNotFoundError, ValueError):
            logger.info(
                f"Cannot import module '{BaseAgentBuilder.__name__}' from path '{agent_directory_path}'. Defaulting to AgentBuilder."
            )
            return AgentBuilder