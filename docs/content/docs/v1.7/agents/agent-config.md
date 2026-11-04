---
sidebar_position: 9
---

# Agent Configuration

The `AgentConfig` is the central configuration system for all agents in the Enthusiast framework. It provides a type-safe, flexible way to configure agent behavior, tools, memory, and dependencies.

## Overview

`AgentConfig` is a Pydantic-based configuration class that defines all aspects of an agent's behavior and capabilities. It serves as the blueprint for building agents with specific configurations while maintaining consistency across the system.

## Core Structure

### Base AgentConfig Class

```python
class AgentConfig(ArbitraryTypeBaseModel, Generic[InjectorT]):
    agent_class: Type[BaseAgent]
    llm: LLMConfig
    repositories: RepositoriesConfig
    retrievers: RetrieversConfig
    injector: Type[InjectorT]
    registry: RegistryConfig
    system_prompt: str
    tools: Optional[list[FunctionToolConfig | LLMToolConfig | AgentToolConfig | FileToolConfig]] = None
    agent_callback_handler: Optional[AgentCallbackHandlerConfig] = None
```

### Configuration Components

#### 1. **agent_class**
- **Type**: `Type[BaseAgent]`
- **Required**: Yes
- **Description**: The specific agent implementation class to instantiate
- **Example**: `ProductSearchAgent`, `UserManualSearchAgent`

#### 2. **llm**
- **Type**: `LLMConfig`
- **Required**: Yes
- **Description**: Language model configuration including model selection and callbacks
- **Components**:
  - `llm_class`: The language model class to use
  - `callbacks`: List of callback handlers for monitoring and logging

#### 3. **repositories**
- **Type**: `RepositoriesConfig`
- **Required**: Yes
- **Description**: Data access layer configuration for all entities
- **Components**:
  - `user`: User repository implementation
  - `message`: Message repository implementation
  - `conversation`: Conversation repository implementation
  - `data_set`: Dataset repository implementation
  - `document_chunk`: Document chunk repository implementation
  - `product`: Product repository implementation
  - `product_chunk`: Product chunk repository implementation
  - `agent`: Agent repository implementation

#### 4. **retrievers**
- **Type**: `RetrieversConfig`
- **Required**: Yes
- **Description**: Document and product retrieval system configuration
- **Components**:
  - `document`: Document retriever configuration
  - `product`: Product retriever configuration

#### 5. **injector**
- **Type**: `Type[InjectorT]`
- **Required**: Yes
- **Description**: Dependency injection container class
- **Example**: `Injector` (default implementation)

#### 6. **registry**
- **Type**: `RegistryConfig`
- **Required**: Yes
- **Description**: Registry configuration for models, LLMs, and embeddings
- **Components**:
  - `llm`: Language model registry configuration
  - `embeddings`: Embedding provider registry configuration
  - `model`: Database model registry configuration

#### 7. **system_prompt**
- **Type**: `str`
- **Required**: Yes
- **Description**: The system prompt passed to the agent. May contain `{variable}` placeholders resolved via the agent's `_get_system_prompt_variables()` hook.

#### 8. **tools**
- **Type**: `Optional[list[FunctionToolConfig | LLMToolConfig | AgentToolConfig]]`
- **Required**: No
- **Description**: List of tools available to the agent
- **Tool Types**:
  - `FunctionToolConfig`: Simple, stateless operations
  - `LLMToolConfig`: AI-powered operations with language models
  - `AgentToolConfig`: Tools that use other agents

#### 9. **memory_compactor_enabled**
- **Type**: `bool`
- **Required**: No (default: `False`)
- **Description**: Enables the memory compactor for this agent. When `True`, an LLM-generated summary of the conversation is persisted every 10 human messages and injected as a `SystemMessage` at the start of each agent call. See [Memory](./memory.md) for details.

#### 10. **agent_callback_handler**
- **Type**: `Optional[AgentCallbackHandlerConfig]`
- **Required**: No
- **Description**: Callback handler for agent-specific events and monitoring

## Default Configuration

The Enthusiast framework provides a comprehensive default configuration that serves as the foundation for all agents. This default configuration is defined in `server/agent/core/agents/default_config.py`.

### Default Configuration Structure

```python
class DefaultAgentConfig(BaseModel):
    repositories: RepositoriesConfig
    retrievers: RetrieversConfig
    injector: Type[Injector]
    registry: RegistryConfig
    llm: LLMConfig
```

### Default Components
Ready to use, built in defaults: 

#### **Repositories**
- **User Repository**: `DjangoUserRepository`
- **Dataset Repository**: `DjangoDataSetRepository`
- **Conversation Repository**: `DjangoConversationRepository`
- **Message Repository**: `DjangoMessageRepository`
- **Product Repository**: `DjangoProductRepository`
- **Document Chunk Repository**: `DjangoDocumentChunkRepository`
- **Product Chunk Repository**: `DjangoProductChunkRepository`
- **Agent Repository**: `DjangoAgentRepository`

#### **Retrievers**
- **Document Retriever**: `DocumentRetriever`
- **Product Retriever**: `ProductRetriever`

#### **Injector**
- **Default Injector**: `Injector` class for dependency management

#### **Registry**
- **LLM Registry**: `LanguageModelRegistry`
- **Embeddings Registry**: `EmbeddingProviderRegistry`
- **Model Registry**: `BaseDjangoSettingsDBModelRegistry`

#### **LLM Configuration**
- **LLM**: `BaseLLM`

## Configuration Provider

Agent configuration is provided through a `BaseAgentConfigProvider` subclass. The framework registry discovers this class automatically at runtime by scanning the agent's package module.

### **Required ConfigProvider Class**

- **Base class**: Must subclass `BaseAgentConfigProvider` from `enthusiast_common.agents`
- **Method**: Must implement `get_config(config_type: ConfigType = ConfigType.CONVERSATION) -> AgentConfigWithDefaults`
- **Discoverability**: Must be importable at the same module level as the agent class path registered in `AVAILABLE_AGENTS`

The registry derives the discovery path from `AVAILABLE_AGENTS`. For example, with `AVAILABLE_AGENTS = ['enthusiast_agent_catalog_enrichment.CatalogEnrichmentAgent']`, the registry strips the class name and imports `enthusiast_agent_catalog_enrichment`, then scans it for any subclass of `BaseAgentConfigProvider`. The first match is used.

There are no restrictions on file naming or directory layout — as long as the `BaseAgentConfigProvider` subclass is importable from that module (e.g. exported via `__init__.py`), the framework will find it.

### **Example**

```python
# config.py
from enthusiast_common.agents import BaseAgentConfigProvider, ConfigType
from enthusiast_common.config import AgentConfigWithDefaults

from .agent import YourAgent
from .prompt import YOUR_AGENT_SYSTEM_PROMPT


class YourAgentConfigProvider(BaseAgentConfigProvider):
    def get_config(self, config_type: ConfigType = ConfigType.CONVERSATION) -> AgentConfigWithDefaults:
        return AgentConfigWithDefaults(
            agent_class=YourAgent,
            system_prompt=YOUR_AGENT_SYSTEM_PROMPT,
            tools=YourAgent.TOOLS,
        )
```

```python
# __init__.py
from .agent import YourAgent
from .config import YourAgentConfigProvider

__all__ = ["YourAgent", "YourAgentConfigProvider"]
```

### **Context-Specific Configuration**

`get_config` receives a `config_type` argument that allows returning a different configuration depending on the call context:

- `ConfigType.CONVERSATION` — interactive user conversations (default)
- `ConfigType.AGENTIC_EXECUTION_DEFINITION` — autonomous agentic execution runs

```python
def get_config(self, config_type: ConfigType = ConfigType.CONVERSATION) -> AgentConfigWithDefaults:
    if config_type == ConfigType.AGENTIC_EXECUTION_DEFINITION:
        return AgentConfigWithDefaults(
            agent_class=YourAgent,
            system_prompt=YOUR_AGENT_EXECUTION_PROMPT,
            tools=YourAgent.TOOLS + [LLMToolConfig(tool_class=StopExecutionTool)],
        )
    return AgentConfigWithDefaults(
        agent_class=YourAgent,
        system_prompt=YOUR_AGENT_SYSTEM_PROMPT,
        tools=YourAgent.TOOLS,
    )
```


## Summary

The `AgentConfig` system provides a robust, flexible, and type-safe way to configure agents in the Enthusiast framework. By understanding its structure, using the default configuration system, and following best practices, developers can create powerful and maintainable agent configurations that leverage the full capabilities of the framework.

Key benefits include:
- **Type Safety**: Pydantic-based validation ensures configuration integrity
- **Flexibility**: Support for custom configurations while maintaining defaults
- **Validation**: Automatic validation of configuration requirements
- **Extensibility**: Easy to add new configuration options and validators
- **Consistency**: Standardized configuration patterns across all agents
