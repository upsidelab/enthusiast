---
sidebar_position: 3
---

# Injector

The Injector class in Enthusiast provides a centralized dependency injection system that gives agents and tools access to all the resources they need to function. It acts as a service locator that manages and provides access to retrievers, repositories, and memory systems.

## Overview

The Injector pattern in Enthusiast serves several key purposes:

- **Centralized Resource Management**: Provides a single point of access to all system resources
- **Dependency Injection**: Eliminates tight coupling between components
- **Resource Sharing**: Allows multiple tools and agents to share the same resources
- **Configuration Management**: Centralizes the configuration of system components

## Architecture

### Base Injector Interface

The `BaseInjector` abstract class defines the contract that all injectors must implement:

```python
class BaseInjector(ABC):
    def __init__(self, repositories: RepositoriesInstances):
        self.repositories = repositories

    @property
    @abstractmethod
    def document_retriever(self) -> BaseVectorStoreRetriever[DocumentChunkDetails]:
        pass

    @property
    @abstractmethod
    def product_retriever(self) -> BaseProductRetriever:
        pass

    @property
    @abstractmethod
    def chat_summary_memory(self) -> BaseMemory:
        pass

    @property
    @abstractmethod
    def chat_limited_memory(self) -> BaseMemory:
        pass
```

### Concrete Injector Implementation

The concrete `Injector` class implements the base interface and provides access to specific implementations:

```python
class Injector(BaseInjector):
    def __init__(
        self,
        document_retriever: BaseVectorStoreRetriever[DocumentChunk],
        product_retriever: BaseProductRetriever,
        repositories: RepositoriesInstances,
        chat_summary_memory: SummaryChatMemory,
        chat_limited_memory: LimitedChatMemory,
    ):
        super().__init__(repositories)
        self._document_retriever = document_retriever
        self._product_retriever = product_retriever
        self._chat_summary_memory = chat_summary_memory
        self._chat_limited_memory = chat_limited_memory

    @property
    def document_retriever(self) -> BaseVectorStoreRetriever[DocumentChunk]:
        return self._document_retriever

    @property
    def product_retriever(self) -> BaseProductRetriever:
        return self._product_retriever

    @property
    def chat_summary_memory(self) -> SummaryChatMemory:
        return self._chat_summary_memory

    @property
    def chat_limited_memory(self) -> LimitedChatMemory:
        return self._chat_limited_memory
```

## Available Resources

### 1. Document Retriever

The document retriever provides access to document content through vector search:

### 2. Product Retriever

The product retriever provides access to product information:

### 3. Chat Memory Systems

The injector provides access to two types of memory systems Summary Chat Memory and Limited Chat Memory:


### 4. Repository Access

The injector provides access to all data repositories:

```python
# Access repositories through injector
repositories = self.injector.repositories

# User repository
user_repo = repositories.user
current_user = user_repo.get_by_id(user_id)

```

## Usage in Tools

### Basic Tool Usage

Tools receive the injector through their constructor and can access all resources:

```python
class ExampleTool(BaseLLMTool):
    def __init__(self, data_set_id: int, llm: BaseLanguageModel, injector: BaseInjector):
        super().__init__(data_set_id=data_set_id, llm=llm, injector=injector)
        self.injector = injector

    def run(self, query: str):
        # Access document retriever
        doc_retriever = self.injector.document_retriever
        relevant_docs = doc_retriever.find_content_matching_query(query)
        
        # Access product retriever
        product_retriever = self.injector.product_retriever
        relevant_products = product_retriever.find_products_matching_query(query)
        
        # Access repositories
        conversation_repo = self.injector.repositories.conversation
        current_conversation = conversation_repo.get_by_id(self.conversation_id)
        
        # Process and return results
        return self._process_results(relevant_docs, relevant_products, current_conversation)
```


## Usage in Agents

### Agent Construction

Agents receive the injector during construction and can access all resources:

```python
class ExampleAgent(BaseAgent):
    def _build_agent_executor(self) -> AgentExecutor:
        tools = self._build_tools()
        agent = create_react_agent(
            tools=tools,
            llm=self._llm,
            prompt=self._prompt,
        )
        return AgentExecutor(agent=agent, tools=tools, memory=self.injector.chat_limited_memory)

```

## Construction and Configuration

### Builder Pattern

The injector is constructed using the agent builder pattern:

```python
def _build_injector(self) -> BaseInjector:
    # Build individual components
    document_retriever = self._build_document_retriever()
    product_retriever = self._build_product_retriever()
    chat_summary_memory = self._build_chat_summary_memory()
    chat_limited_memory = self._build_chat_limited_memory()
    
    # Create injector with all components
    return self._config.injector(
        product_retriever=product_retriever,
        document_retriever=document_retriever,
        repositories=self._repositories,
        chat_summary_memory=chat_summary_memory,
        chat_limited_memory=chat_limited_memory,
    )
```


## Extending the Injector

### Custom Injector Implementation

```python
class CustomInjector(BaseInjector):
    def __init__(self, repositories: RepositoriesInstances, custom_service: CustomService):
        super().__init__(repositories)
        self._custom_service = custom_service

    @property
    def document_retriever(self) -> BaseVectorStoreRetriever[DocumentChunkDetails]:
        return self._build_custom_document_retriever()

    @property
    def product_retriever(self) -> BaseProductRetriever:
        return self._build_custom_product_retriever()

    @property
    def chat_summary_memory(self) -> BaseMemory:
        return self._build_custom_summary_memory()

    @property
    def chat_limited_memory(self) -> BaseMemory:
        return self._build_custom_limited_memory()

    @property
    def custom_service(self) -> CustomService:
        return self._custom_service
```

### Adding New Resources

```python
class ExtendedInjector(Injector):
    def __init__(self, *args, analytics_service: AnalyticsService, **kwargs):
        super().__init__(*args, **kwargs)
        self._analytics_service = analytics_service

    @property
    def analytics_service(self) -> AnalyticsService:
        return self._analytics_service
```

## Summary

The Injector class in Enthusiast provides a comprehensive dependency injection system that:

- **Centralizes Resource Management**: All system resources are accessible through a single interface
- **Enables Loose Coupling**: Components don't need to know how to create their dependencies
- **Provides Type Safety**: All resources are properly typed and validated

By using the injector pattern, tools and agents can focus on their core logic while the injector handles all the complexity of resource management and dependency resolution.
