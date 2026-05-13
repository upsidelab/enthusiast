from abc import ABC, abstractmethod
from enum import StrEnum

from ..config import AgentConfig


class ConfigType(StrEnum):
    """Registry of valid agent configuration context types."""

    CONVERSATION = "conversation"
    AGENTIC_EXECUTION_DEFINITION = "agentic_execution_definition"


class BaseAgentConfigProvider(ABC):
    """Interface for providing agent configuration based on the call context.

    Agent plugins export a subclass of this from their ``__init__.py``. The
    agent registry discovers it at runtime and calls :meth:`get_config` with
    the appropriate ``config_type`` so the plugin can return a context-specific
    configuration (e.g. a different system prompt for agentic execution runs).

    Plugins that do not need context-specific configs can ignore the
    ``config_type`` argument and always return the same configuration.
    """

    @abstractmethod
    def get_config(self, config_type: ConfigType = ConfigType.CONVERSATION) -> AgentConfig:
        """Return the agent configuration for the given context type.

        Args:
            config_type: :attr:`ConfigType.CONVERSATION` for interactive user
                conversations, :attr:`ConfigType.AGENTIC_EXECUTION_DEFINITION` for
                autonomous agentic execution runs.

        Returns:
            AgentConfig: fully populated configuration ready for the builder.
        """
        pass
