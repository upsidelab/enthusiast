import inspect
import logging
from abc import ABC, abstractmethod
from importlib import import_module
from typing import Any, Type, TypeVar

from django.conf import settings
from enthusiast_common.agents import BaseAgent
from enthusiast_common.builder import BaseAgentBuilder
from enthusiast_common.config.base import AgentConfig
from enthusiast_common.structures import LLMFile

from agent.core.agents.default_config import merge_config
from agent.core.builder import AgentBuilder
from agent.models import Conversation

T = TypeVar("T", bound=BaseAgentBuilder)

logger = logging.getLogger(__name__)


class AgentRegistryError(Exception):
    """Base exception for all AgentRegistry errors."""


class AgentNotFoundError(AgentRegistryError):
    """Raised when agent type is not found in config."""


class AgentConfigError(AgentRegistryError):
    """Raised when agent configuration is missing or invalid."""


class AgentImportError(AgentRegistryError):
    """Raised when an agent module or class cannot be imported."""


class BaseAgentRegistry(ABC):
    def __init__(self, agents_config: dict[Any, Any]):
        self._agents_config = agents_config

    @abstractmethod
    def get_conversation_agent(self, *args, **kwargs) -> BaseAgent:
        pass

    @abstractmethod
    def get_agent_class_by_type(self, *args, **kwargs) -> Type[BaseAgent]:
        pass


class AgentRegistry(BaseAgentRegistry):
    def __init__(self):
        agents_config = settings.AVAILABLE_AGENTS
        super().__init__(agents_config)

    def get_conversation_agent(self, conversation: Conversation, streaming: bool, files: list[LLMFile]) -> BaseAgent:
        try:
            builder = self._get_builder_class_by_name(agent_type=conversation.agent.agent_type)
            config = self._get_config_by_name(agent_type=conversation.agent.agent_type)
            config = merge_config(partial=config)
            return builder(config=config, conversation_id=conversation.id, streaming=streaming, files=files).build()
        except Exception as e:
            raise AgentRegistryError(f"Failed to build agent for conversation {conversation.id}") from e

    def get_agent_class_by_type(self, agent_type: str) -> Type[BaseAgent]:
        agent_directory_path = self._get_agent_directory_path(agent_type)
        agent_module_path = f"{agent_directory_path}.agent"
        try:
            agent_module = import_module(agent_module_path)
        except ModuleNotFoundError as e:
            raise AgentImportError(f"Cannot import module '{agent_module_path}' for agent '{agent_type}'.") from e

        agents = [
            cls
            for _, cls in inspect.getmembers(agent_module, inspect.isclass)
            if issubclass(cls, BaseAgent) and cls.__module__ == agent_module.__name__
        ]
        if not agents:
            raise AgentNotFoundError(f"No valid agent classes found in module '{agent_module_path}'.")
        return agents[0]

    def _get_agent_directory_path(self, agent_type: str) -> str:
        try:
            agent_settings = self._agents_config[agent_type]
        except KeyError as e:
            raise AgentNotFoundError(f"Agent '{agent_type}' is not defined in settings.AVAILABLE_AGENTS.") from e
        try:
            return agent_settings["agent_directory_path"]
        except KeyError as e:
            raise AgentConfigError(f"agent_directory_path is not defined for key: '{agent_type}'") from e

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
        builder_module_path = f"{agent_directory_path}.builder"
        try:
            builder_module = import_module(builder_module_path)
        except ModuleNotFoundError:
            logger.info(
                f"Cannot import module '{builder_module_path}' for agent '{agent_type}'. Defaulting to AgentBuilder."
            )
            return AgentBuilder

        try:
            builder_class = getattr(builder_module, "Builder")
        except AttributeError as e:
            raise AgentImportError(f"Module '{builder_module_path}' has no attribute 'Builder'.") from e

        return builder_class
