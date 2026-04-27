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
    def chat_history(self) -> BaseChatMessageHistory:
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
        chat_history: BaseChatMessageHistory,
    ):
        super().__init__(repositories)
        self._document_retriever = document_retriever
        self._product_retriever = product_retriever
        self._chat_history = chat_history

    @property
    def document_retriever(self) -> BaseVectorStoreRetriever[DocumentChunk]:
        return self._document_retriever

    @property
    def product_retriever(self) -> BaseProductRetriever:
        return self._product_retriever

    @property
    def chat_history(self) -> BaseChatMessageHistory:
        return self._chat_history
```

## Available Resources

### 1. Document Retriever

The document retriever provides access to document content through vector search:

### 2. Product Retriever

The product retriever provides access to product information:

### 3. Chat History

The injector provides access to the persistent conversation history via `chat_history: BaseChatMessageHistory`. See [Memory](./memory.md) for details on token limiting and persistence.


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
class ExampleAgent(BaseToolCallingAgent):
    def get_answer(self, input_text: str) -> str:
        # Fetch relevant documents before invoking the agent
        # and inject them as additional context into the user message
        docs = self._injector.document_retriever.find_content_matching_query(input_text)
        context = "\n".join(doc.content for doc in docs)
        enriched_input = f"{input_text}\n\nContext:\n{context}"
        return super().get_answer(enriched_input)

```

## Construction and Configuration

### Builder Pattern

The injector is constructed using the agent builder pattern:

```python
def _build_injector(self) -> BaseInjector:
    # Build individual components
    document_retriever = self._build_document_retriever()
    product_retriever = self._build_product_retriever()
    chat_history = self._build_chat_history()

    # Create injector with all components
    return self._config.injector(
        product_retriever=product_retriever,
        document_retriever=document_retriever,
        repositories=self._repositories,
        chat_history=chat_history,
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
    def chat_history(self) -> BaseChatMessageHistory:
        return self._build_custom_chat_history()

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
