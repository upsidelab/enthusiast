---
sidebar_position: 3
---

# Memory Types

Enthusiast provides by default two memory management strategies to help agents maintain context and conversation history. Each memory type is designed for different use cases and performance requirements.

## Overview

Memory in Enthusiast serves two main purposes:
1. **Conversation Persistence**: Storing and retrieving chat history from the database
2. **Context Management**: Providing relevant conversation context to agents while managing token limits

## Available Memory Types

### 1. Summary Chat Memory

**Class**: `SummaryChatMemory`  
**Base**: `ConversationSummaryBufferMemory` with intermediate steps persistence

**Description**: This memory type automatically summarizes conversation history when it exceeds the token limit, ensuring agents always have relevant context without hitting token constraints.

**Key Features**:
- Automatically summarizes long conversations
- Persists intermediate agent steps (tool calls, observations)
- Configurable token limit (default: 3000 tokens)
- Maintains conversation flow while optimizing memory usage

**Best For**:
- Long-running conversations
- Agents that need to remember key points from extended discussions
- Scenarios where conversation context is important but token efficiency is required

**Configuration**:
```python
SummaryChatMemory(
    llm=language_model,
    memory_key="chat_history",
    return_messages=True,
    max_token_limit=3000,
    output_key="output",
    chat_memory=persistent_history
)
```

### 2. Limited Chat Memory

**Class**: `LimitedChatMemory`  
**Base**: `ConversationTokenBufferMemory` with intermediate steps persistence

**Description**: This memory type maintains a fixed token limit for conversation history, automatically truncating older messages when the limit is exceeded.

**Key Features**:
- Fixed token limit for conversation context
- Persists intermediate agent steps
- Configurable token limit (default: 3000 tokens)
- Predictable memory usage

**Best For**:
- Real-time applications with strict token budgets
- Scenarios where recent context is more important than historical context
- High-frequency chat applications

**Configuration**:
```python
LimitedChatMemory(
    llm=language_model,
    memory_key="chat_history",
    return_messages=True,
    max_token_limit=3000,
    output_key="output",
    chat_memory=persistent_history
)
```

## Configuration

### Default Settings

- **Token Limit**: 3000 tokens (configurable)
- **Memory Key**: "chat_history"
- **Output Key**: "output"
- **Message Return**: True (returns structured messages)

### Customization

In need of customization, those classes may be changed inside builder's methods responsible for creating it.
```python
    def _build_chat_summary_memory(self) -> SummaryChatMemory:
        history = PersistentChatHistory(self._repositories.conversation, self._config.conversation_id)
        return SummaryChatMemory(
            llm=self._llm,
            memory_key="chat_history",
            return_messages=True,
            max_token_limit=3000,
            output_key="output",
            chat_memory=history,
        )

    def _build_chat_limited_memory(self) -> LimitedChatMemory:
        history = PersistentChatHistory(self._repositories.conversation, self._config.conversation_id)
        return LimitedChatMemory(
            llm=self._llm,
            memory_key="chat_history",
            return_messages=True,
            max_token_limit=3000,
            output_key="output",
            chat_memory=history,
        )
```

## Additional memory
In order to add additional type of memory:
Create custom memory class and then, build custom Injector based on enthusiast-common interface - `BaseInjector`:
```python
class Injector(BaseInjector):
    def __init__(
        self,
        document_retriever: BaseRetriever,
        product_retriever: BaseRetriever,
        repositories: RepositoriesInstances,
        chat_summary_memory: SummaryChatMemory,
        chat_limited_memory: LimitedChatMemory,
        additional_memory: AdditionalMemoryClass,
    ):
        super().__init__(repositories)
        self._document_retriever = document_retriever
        self._product_retriever = product_retriever
        self._chat_summary_memory = chat_summary_memory
        self._chat_limited_memory = chat_limited_memory
        self._additional_memory = additional_memory

    @property
    def document_retriever(self) -> BaseRetriever:
        return self._document_retriever

    @property
    def product_retriever(self) -> BaseRetriever:
        return self._product_retriever

    @property
    def chat_summary_memory(self) -> SummaryChatMemory:
        return self._chat_summary_memory

    @property
    def chat_limited_memory(self) -> LimitedChatMemory:
        return self._chat_limited_memory

    @property
    def additional_memory(self) -> AdditionalMemory:
        return self.additional_memory
```
Add method to build memory class instance inside Builder:
```python
    def _build_additional_memory(self) -> AdditionalMemory:
        history = PersistentChatHistory(self._repositories.conversation, self._config.conversation_id)
        return AdditionalMemory(
            llm=self._llm,
            memory_key="chat_history",
            return_messages=True,
            max_token_limit=3000,
            output_key="output",
            chat_memory=history,
        )
```
Add it to injector:

```python
    def _build_injector(self) -> BaseInjector:
        document_retriever = self._build_document_retriever()
        product_retriever = self._build_product_retriever()
        chat_summary_memory = self._build_chat_summary_memory()
        chat_limited_memory = self._build_chat_limited_memory()
        additional_memory = self._build_additional_memory()
        return self._config.injector(
            product_retriever=product_retriever,
            document_retriever=document_retriever,
            repositories=self._repositories,
            chat_summary_memory=chat_summary_memory,
            chat_limited_memory=chat_limited_memory,
            additional_memory=additional_memory
        )
```
## Usage Examples

### Basic Memory Usage
All memory instances are accessible inside Agent class via `self.injector`
```python
from enthusiast_common.agents import BaseAgent
from langchain.agents import AgentExecutor, create_react_agent

class MyAgent(BaseAgent):
    def _build_agent_executor(self) -> AgentExecutor:
        tools = self._build_tools()
        agent = create_react_agent(
            tools=tools,
            llm=self._llm,
            prompt=self._prompt,
        )
        return AgentExecutor(agent=agent, tools=tools, memory=self.injector.chat_limited_memory)
```
