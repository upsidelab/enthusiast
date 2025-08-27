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
    prompt_template: Optional[PromptTemplateConfig] = None
    chat_prompt_template: Optional[ChatPromptTemplateConfig] = None
    tools: Optional[list[FunctionToolConfig | LLMToolConfig | AgentToolConfig]] = None
    agent_callback_handler: Optional[AgentCallbackHandlerConfig] = None
```

### Configuration Components

#### 1. **agent_class**
- **Type**: `Type[BaseAgent]`
- **Required**: Yes
- **Description**: The specific agent implementation class to instantiate
- **Example**: `ProductSearchReActAgent`, `ToolCallingAgent`

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

#### 7. **prompt_template** / **chat_prompt_template**
- **Type**: `PromptTemplateConfig` or `ChatPromptTemplateConfig`
- **Required**: Exactly one must be provided
- **Description**: Prompt configuration for agent behavior and instructions
- **Validation**: The system ensures exactly one prompt type is configured

#### 8. **tools**
- **Type**: `Optional[list[FunctionToolConfig | LLMToolConfig | AgentToolConfig]]`
- **Required**: No
- **Description**: List of tools available to the agent
- **Tool Types**:
  - `FunctionToolConfig`: Simple, stateless operations
  - `LLMToolConfig`: AI-powered operations with language models
  - `AgentToolConfig`: Tools that use other agents

#### 9. **agent_callback_handler**
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

## Configuration File Placement

Understanding where to place configuration files is crucial for the Enthusiast framework to properly discover and load your agent configurations. The framework follows a specific directory structure and import pattern.

### **Directory Structure Requirements**

The Enthusiast framework expects agent configurations to be organized in a specific directory structure:

```
your_project/
├── your_agent_package/
│   ├── __init__.py
│   ├── agent.py          # Agent implementation
│   ├── config.py         # Configuration file (REQUIRED)
```

### **Required Configuration File**

- **File Name**: `config.py`
- **Location**: Must be in the same directory as your agent implementation
- **Function Name**: Must contain a function named `get_config()`
- **Return Type**: Must return `AgentConfigWithDefaults`


## Summary

The `AgentConfig` system provides a robust, flexible, and type-safe way to configure agents in the Enthusiast framework. By understanding its structure, using the default configuration system, and following best practices, developers can create powerful and maintainable agent configurations that leverage the full capabilities of the framework.

Key benefits include:
- **Type Safety**: Pydantic-based validation ensures configuration integrity
- **Flexibility**: Support for custom configurations while maintaining defaults
- **Validation**: Automatic validation of configuration requirements
- **Extensibility**: Easy to add new configuration options and validators
- **Consistency**: Standardized configuration patterns across all agents
