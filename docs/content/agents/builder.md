---
sidebar_position: 5
---

# Builder

The Builder pattern in Enthusiast provides a systematic approach to constructing complex agent instances with all their dependencies. The system consists of an abstract `BaseAgentBuilder` class that defines the construction interface and a concrete `AgentBuilder` implementation that handles the specific construction logic.

## Overview

The Builder system serves several key purposes:

- **Complex Object Construction**: Manages the creation of agents with multiple dependencies
- **Dependency Resolution**: Handles the creation and configuration of all agent components
- **Configuration Management**: Translates configuration objects into concrete instances
- **Resource Assembly**: Coordinates the assembly of tools, memory systems, and services

## Base Agent Builder

### Abstract Interface

The `BaseAgentBuilder` defines the contract that all agent builders must implement:

```python
class BaseAgentBuilder(ABC, Generic[ConfigT]):
    def __init__(self, config: ConfigT, conversation_id: Any, streaming: bool = False):
        self._llm = None
        self._embeddings_registry = None
        self._data_set_id = None
        self._injector = None
        self._config = config
        self.conversation_id = conversation_id
        self.streaming = streaming

    def build(self) -> BaseAgent:
        """Main build method that orchestrates the construction process"""
        # Build sequence implementation...
```

### Build Process

The main `build()` method orchestrates the construction process:

```python
def build(self) -> BaseAgent:
    # 1. Build registries and repositories
    model_registry = self._build_db_models_registry()
    self._build_and_set_repositories(model_registry)
    self._data_set_id = self._repositories.conversation.get_data_set_id(self.conversation_id)
    
    # 2. Build core components
    self._llm = self._build_llm(self._config.llm)
    self._embeddings_registry = self._build_embeddings_registry()
    self._injector = self._build_injector()
    
    # 3. Build tools and handlers
    tools = self._build_tools(default_llm=self._llm, injector=self._injector)
    agent_callback_handler = self._build_agent_callback_handler()
    prompt_template = self._build_prompt_template()
    
    # 4. Create and configure agent
    agent_instance = self._build_agent(tools, self._llm, prompt_template, agent_callback_handler)
    self._inject_additional_arguments(agent_instance)
    
    return agent_instance
```

### Abstract Methods

The base builder defines several abstract methods that concrete implementations must provide:

#### Core Construction Methods

```python
@abstractmethod
def _build_agent(
    self,
    tools: list[BaseTool],
    llm: BaseLanguageModel,
    prompt: PromptTemplate | ChatMessagePromptTemplate,
    callback_handler: BaseCallbackHandler,
) -> BaseAgent:
    """Build the final agent instance"""
    pass

@abstractmethod
def _build_injector(self) -> BaseInjector:
    """Build the dependency injection container"""
    pass

@abstractmethod
def _build_prompt_template(self) -> BasePromptTemplate:
    """Build the prompt template for the agent"""
    pass
```

#### Registry and Repository Methods

```python
@abstractmethod
def _build_llm_registry(self) -> BaseLanguageModelRegistry:
    """Build the language model registry"""
    pass

@abstractmethod
def _build_db_models_registry(self) -> BaseDBModelsRegistry:
    """Build the database models registry"""
    pass

@abstractmethod
def _build_and_set_repositories(self, models_registry: BaseDBModelsRegistry) -> None:
    """Build and configure data repositories"""
    pass

@abstractmethod
def _build_embeddings_registry(self) -> BaseEmbeddingProviderRegistry:
    """Build the embeddings provider registry"""
    pass
```

#### Component Construction Methods

```python
@abstractmethod
def _build_llm(self, llm_config: LLMConfig) -> BaseLanguageModel:
    """Build the language model instance"""
    pass

@abstractmethod
def _build_default_llm(self) -> BaseLanguageModel:
    """Build the default language model for tools"""
    pass

@abstractmethod
def _build_tools(self, default_llm: BaseLanguageModel, injector: BaseInjector) -> list[BaseTool]:
    """Build all agent tools"""
    pass

@abstractmethod
def _build_function_tool(self, config: FunctionToolConfig) -> BaseFunctionTool:
    """Build function-based tools"""
    pass

@abstractmethod
def _build_llm_tool(self, config: LLMToolConfig, default_llm: BaseLanguageModel, injector: BaseInjector) -> BaseLLMTool:
    """Build LLM-powered tools"""
    pass

@abstractmethod
def _build_agent_tool(self, config: AgentToolConfig) -> BaseAgentTool:
    """Build agent-based tools"""
    pass
```

#### Memory and Callback Methods

```python
@abstractmethod
def _build_agent_callback_handler(self) -> Optional[BaseCallbackHandler]:
    """Build the agent callback handler"""
    pass

@abstractmethod
def _build_llm_callback_handlers(self) -> Optional[BaseCallbackHandler]:
    """Build LLM callback handlers"""
    pass

@abstractmethod
def _build_chat_summary_memory(self) -> BaseMemory:
    """Build summary-based chat memory"""
    pass

@abstractmethod
def _build_chat_limited_memory(self) -> BaseMemory:
    """Build limited chat memory"""
    pass
```

### Runtime Configuration Injection

The builder automatically injects runtime configuration into constructed agents:

```python
def _inject_additional_arguments(self, agent_instance: BaseAgent) -> None:
    """Inject runtime configuration from the database"""
    agent_configuration_id = self._repositories.conversation.get_agent_id(self.conversation_id)
    runtime_arguments = self._repositories.agent.get_agent_configuration_by_id(agent_configuration_id)
    agent_instance.set_runtime_arguments(runtime_arguments)
```

## Agent Builder Implementation

### Concrete Implementation

The `AgentBuilder` class provides the concrete implementation of all abstract methods, which will be a default builder for all agents, unless custom one is provided:


## Usage Patterns

### Basic Usage

```python
# Create builder with configuration
builder = AgentBuilder(
    config=agent_config,
    conversation_id="conversation_123",
    streaming=False
)

# Build the agent
agent = builder.build()

# Use the agent
response = agent.get_answer("Hello, how can you help me?")
```

## Summary

The Builder system in Enthusiast provides a comprehensive and flexible approach to agent construction:

- **BaseAgentBuilder**: Abstract interface defining the construction contract
- **AgentBuilder**: Concrete implementation handling all construction details
- **Systematic Construction**: Step-by-step assembly of all agent components
- **Configuration-Driven**: All construction driven by configuration objects
- **Dependency Management**: Automatic resolution and assembly of dependencies
- **Runtime Configuration**: Dynamic configuration injection after construction
- **Extensibility**: Easy creation of custom builders for specialized agents

By using the Builder pattern, Enthusiast ensures that complex agents are constructed consistently, reliably, and with all necessary dependencies properly configured and connected.
