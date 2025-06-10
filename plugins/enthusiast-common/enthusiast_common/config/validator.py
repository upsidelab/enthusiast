import logging
from typing import Optional, Type

from .base import BaseAgent
from ..config import AgentConfig, LLMConfig, RegistryConfig, RepositoriesConfig, RetrieversConfig
from ..injectors import BaseInjector
from ..services.conversation import ConversationService
from ..tools import BaseAgentTool, BaseLLMTool, BaseFunctionTool


logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Raised when configuration validation fails"""

    pass


class ConfigValidationResult:
    """Result of configuration validation"""

    def __init__(self):
        self.is_valid = True
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def add_error(self, message: str):
        self.errors.append(message)
        self.is_valid = False

    def add_warning(self, message: str):
        self.warnings.append(message)

    def __bool__(self):
        return self.is_valid

    def __str__(self):
        lines = []
        if self.errors:
            lines.append("Errors:")
            lines.extend(f"  - {error}" for error in self.errors)
        if self.warnings:
            lines.append("Warnings:")
            lines.extend(f"  - {warning}" for warning in self.warnings)
        return "\n".join(lines)


class AgentConfigValidator:
    """Validates AgentConfig instances for completeness and correctness"""

    def __init__(self, strict: bool = True):
        """
        Args:
            strict: If True, warnings are treated as errors
        """
        self.strict = strict

    def validate(self, config: AgentConfig) -> ConfigValidationResult:
        """
        Validate the entire configuration

        Args:
            config: The configuration to validate

        Returns:
            ConfigValidationResult with validation status and messages
        """
        result = ConfigValidationResult()

        if config is None:
            result.add_error("Configuration cannot be None")
            return result
        self._validate_core_fields(config, result)
        self._validate_registry_config(config.registry, result)
        self._validate_llm_config(config.llm, result)
        self._validate_repositories_config(config.repositories, result)
        self._validate_retrievers_config(config.retrievers, result)
        self._validate_tools_config(config, result)
        self._validate_injector_config(config.injector, result)
        if self.strict and result.warnings:
            for warning in result.warnings:
                result.add_error(f"Strict mode: {warning}")
            result.warnings.clear()

        return result

    def validate_or_raise(self, config: AgentConfig):
        """
        Validate configuration and raise ValidationError if invalid

        Args:
            config: The configuration to validate

        Raises:
            ValidationError: If configuration is invalid
        """
        result = self.validate(config)
        if not result.is_valid:
            raise ValidationError(f"Configuration validation failed:\n{result}")

        if result.warnings:
            logger.warning(f"Configuration validation warnings:\n{result}")

    def _validate_core_fields(self, config: AgentConfig, result: ConfigValidationResult):
        """Validate core required fields"""
        if not isinstance(config.conversation_id, int):
            result.add_error("conversation_id must be an integer")
        elif config.conversation_id <= 0:
            result.add_error("conversation_id must be positive")

        if not config.prompt_template:
            result.add_error("prompt_template is required")

        if not config.agent_class:
            result.add_error("agent_class is required")
        elif not issubclass(config.agent_class, BaseAgent):
            result.add_error("agent_class must be a subclass of BaseAgent")

        if not config.conversation_service:
            result.add_error("conversation_service is required")
        elif not issubclass(config.conversation_service, ConversationService):
            result.add_error("conversation_service must be a subclass of ConversationService")

    def _validate_registry_config(self, registry: RegistryConfig, result: ConfigValidationResult):
        """Validate registry configuration"""
        if not registry:
            result.add_error("registry configuration is required")
            return
        if not registry.llm:
            result.add_error("registry.llm configuration is required")
        elif not registry.llm.registry_class:
            result.add_error("registry.llm.registry_class is required")
        if not registry.embeddings:
            result.add_error("registry.embeddings configuration is required")
        elif not registry.embeddings.registry_class:
            result.add_error("registry.embeddings.registry_class is required")
        if not registry.model:
            result.add_error("registry.model configuration is required")
        elif not registry.model.registry_class:
            result.add_error("registry.model.registry_class is required")

    def _validate_llm_config(self, llm_config: LLMConfig, result: ConfigValidationResult):
        """Validate LLM configuration"""
        if not llm_config:
            result.add_error("llm configuration is required")
            return

        if not llm_config.model_class:
            result.add_error("llm.model_class is required")
        if llm_config.callbacks is not None and not isinstance(llm_config.callbacks, list):
            result.add_error("llm.callbacks must be a list if provided")
        if not isinstance(llm_config.streaming, bool):
            result.add_warning("llm.streaming should be a boolean")

    def _validate_repositories_config(self, repositories: RepositoriesConfig, result: ConfigValidationResult):
        """Validate repositories configuration"""
        if not repositories:
            result.add_error("repositories configuration is required")
            return

        required_repos = ["user", "message", "conversation", "data_set", "document_chunk", "product"]

        for repo_name in required_repos:
            if not hasattr(repositories, repo_name):
                result.add_error(f"repositories.{repo_name} is required")
            else:
                repo_class = getattr(repositories, repo_name)
                if not repo_class:
                    result.add_error(f"repositories.{repo_name} cannot be None")

    def _validate_retrievers_config(self, retrievers: RetrieversConfig, result: ConfigValidationResult):
        """Validate retrievers configuration"""
        if not retrievers:
            result.add_error("retrievers configuration is required")
            return
        if not retrievers.product:
            result.add_error("retrievers.product configuration is required")
        elif not retrievers.product.retriever_class:
            result.add_error("retrievers.product.retriever_class is required")
        else:
            if retrievers.product.number_of_products is not None:
                if (
                    not isinstance(retrievers.product.number_of_products, int)
                    or retrievers.product.number_of_products <= 0
                ):
                    result.add_error("retrievers.product.number_of_products must be a positive integer")

            if retrievers.product.max_sample_products is not None:
                if (
                    not isinstance(retrievers.product.max_sample_products, int)
                    or retrievers.product.max_sample_products <= 0
                ):
                    result.add_error("retrievers.product.max_sample_products must be a positive integer")
        if not retrievers.document:
            result.add_error("retrievers.document configuration is required")
        elif not retrievers.document.retriever_class:
            result.add_error("retrievers.document.retriever_class is required")
        else:
            if retrievers.document.max_documents is not None:
                if not isinstance(retrievers.document.max_documents, int) or retrievers.document.max_documents <= 0:
                    result.add_error("retrievers.document.max_documents must be a positive integer")

    def _validate_tools_config(self, config: AgentConfig, result: ConfigValidationResult):
        """Validate tools configuration"""
        if config.function_tools:
            if not isinstance(config.function_tools, list):
                result.add_error("function_tools must be a list")
            else:
                for i, tool_class in enumerate(config.function_tools):
                    if not tool_class:
                        result.add_error(f"function_tools[{i}] cannot be None")
                    elif not issubclass(tool_class, BaseFunctionTool):
                        result.add_error(f"function_tools[{i}] must be a subclass of BaseFunctionTool")
        if config.llm_tools:
            if not isinstance(config.llm_tools, list):
                result.add_error("llm_tools must be a list")
            else:
                for i, tool_config in enumerate(config.llm_tools):
                    if not tool_config:
                        result.add_error(f"llm_tools[{i}] cannot be None")
                    elif not tool_config.model_class:
                        result.add_error(f"llm_tools[{i}].model_class is required")
                    elif not issubclass(tool_config.model_class, BaseLLMTool):
                        result.add_error(f"llm_tools[{i}].model_class must be a subclass of BaseLLMTool")
        if config.agent_tools:
            if not isinstance(config.agent_tools, list):
                result.add_error("agent_tools must be a list")
            else:
                for i, tool_config in enumerate(config.agent_tools):
                    if not tool_config:
                        result.add_error(f"agent_tools[{i}] cannot be None")
                    elif not tool_config.model_class:
                        result.add_error(f"agent_tools[{i}].model_class is required")
                    elif not issubclass(tool_config.model_class, BaseAgentTool):
                        result.add_error(f"agent_tools[{i}].model_class must be a subclass of BaseAgentTool")
        if not any([config.function_tools, config.llm_tools, config.agent_tools]):
            result.add_warning("No tools configured - agent may have limited functionality")

    def _validate_injector_config(self, injector_class: Optional[Type[BaseInjector]], result: ConfigValidationResult):
        """Validate injector configuration"""
        if not injector_class:
            result.add_error("injector is required")
        elif not issubclass(injector_class, BaseInjector):
            result.add_error("injector must be a subclass of BaseInjector")
