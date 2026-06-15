---
sidebar_position: 3
---

# Memory

Enthusiast manages conversation memory through two complementary mechanisms: **persistent chat history** and an optional **memory compactor**. Together they ensure agents have accurate, token-efficient access to conversation context.

## Overview

Memory in Enthusiast serves two main purposes:
1. **Conversation Persistence**: Storing and retrieving chat history from the database via `PersistentChatHistory`
2. **Context Management**: Assembling the right messages for each LLM call via `ContextWindowBuilder`

On every agent invocation the context window is built as follows:

```
[SystemMessage: summary of earlier conversation]   ← only when compactor has a summary
[trim_messages: most recent 3000 tokens of history]
[new HumanMessage]
```

## Chat History

**Class**: `PersistentChatHistory`  
**Base**: `BaseChatMessageHistory`

`PersistentChatHistory` stores all conversation messages in the database and is the single source of truth for chat history. It is injected into every agent via the `chat_history` property on `BaseInjector`.

**Key Features**:
- Persists all message types: human, AI, tool calls, tool results, intermediate steps
- Interleaves parallel tool calls with their results for correct reconstruction
- Provides `messages_after(message_id)` for incremental compaction
- Accessible via `self._injector.chat_history` inside an agent

## Context Window

**Class**: `ContextWindowBuilder`

`ContextWindowBuilder` assembles the list of messages passed to the LLM on each agent call. It trims history to fit the token budget and optionally prepends a summary from the memory compactor.

**Key Features**:
- Trims history to the most recent 3000 tokens using `strategy="last"`
- Prepends a `SystemMessage` with the compacted summary when one is available
- Token counting uses an approximate counter

**Configuration**:
```python
MAX_HISTORY_TOKENS = 3000  # configurable in base_tool_calling_agent.py

context_messages = ContextWindowBuilder(
    chat_history=self._injector.chat_history,
    memory_compactor=self._injector.memory_compactor,
).build(max_tokens=MAX_HISTORY_TOKENS)
```

## Memory Compactor

The memory compactor is an optional mechanism that generates an LLM-based summary of the conversation and persists it to the database. It ensures that context beyond the token-trimming window is not silently lost.

### How it works

Every **10 human messages**, the compactor invokes the LLM to produce a summary of the conversation so far. The summary is stored on the `Conversation` record and injected as a `SystemMessage` at the start of each subsequent agent call:

```
[SystemMessage: summary of earlier conversation]
[trim_messages: most recent 3000 tokens]
[new HumanMessage]
```

Summarisation is **incremental** — subsequent compactions send only the new messages alongside the existing summary, so the cost of each compaction stays constant regardless of conversation length.

### Enabling the compactor

The compactor is opt-in per agent type via `memory_compactor_enabled` in `AgentConfig`. Set it to `True` in the `AgentConfigWithDefaults` returned from your agent's `get_config()`:

```python
# your_agent/config.py

def get_config() -> AgentConfigWithDefaults:
    return AgentConfigWithDefaults(
        agent_class=MyAgent,
        system_prompt="...",
        tools=[...],
        memory_compactor_enabled=True,
    )
```

No agent gets a compactor unless it explicitly opts in.

## Customization

### Custom Injector

`BaseInjector` exposes `chat_history` (required) and `memory_compactor` (optional). Custom injectors must implement `chat_history`:

```python
from enthusiast_common.injectors import BaseInjector
from enthusiast_common.memory import BaseMemoryCompactor
from langchain_core.chat_history import BaseChatMessageHistory
from typing import Optional

class Injector(BaseInjector):
    def __init__(
        self,
        document_retriever: BaseRetriever,
        product_retriever: BaseRetriever,
        repositories: RepositoriesInstances,
        chat_history: BaseChatMessageHistory,
        memory_compactor: Optional[BaseMemoryCompactor] = None,
    ):
        super().__init__(repositories)
        self._document_retriever = document_retriever
        self._product_retriever = product_retriever
        self._chat_history = chat_history
        self._memory_compactor = memory_compactor

    @property
    def document_retriever(self) -> BaseRetriever:
        return self._document_retriever

    @property
    def product_retriever(self) -> BaseRetriever:
        return self._product_retriever

    @property
    def chat_history(self) -> BaseChatMessageHistory:
        return self._chat_history

    @property
    def memory_compactor(self) -> Optional[BaseMemoryCompactor]:
        return self._memory_compactor
```

### Custom Memory Compactor

To implement a custom compactor, subclass `BaseMemoryCompactor` from `enthusiast-common`:

```python
from enthusiast_common.memory import BaseMemoryCompactor
from typing import Optional

class MyMemoryCompactor(BaseMemoryCompactor):
    def get_summary(self) -> Optional[str]:
        """Return the persisted summary, or None if not yet generated."""
        ...

    def compact_if_needed(self) -> None:
        """Generate and persist a new summary when the threshold is reached."""
        ...
```

Build it in your `AgentBuilder` and pass it to the injector:

```python
class MyAgentBuilder(BaseAgentBuilder):
    def _build_injector(self) -> BaseInjector:
        chat_history = self._build_chat_history()
        memory_compactor = MyMemoryCompactor(...) if self._config.memory_compactor_enabled else None
        return self._config.injector(
            product_retriever=self._build_product_retriever(),
            document_retriever=self._build_document_retriever(),
            repositories=self._repositories,
            chat_history=chat_history,
            memory_compactor=memory_compactor,
        )
```

## Usage Examples

### Accessing chat history in an agent

`chat_history` is accessible via `self._injector` inside any agent class:

```python
from enthusiast_common.agents import BaseAgent
from langchain_core.messages import HumanMessage

class MyAgent(BaseAgent):
    def get_answer(self, input_text: str) -> str:
        history = self._injector.chat_history
        context = ContextWindowBuilder(
            chat_history=history,
            memory_compactor=self._injector.memory_compactor,
        ).build(max_tokens=3000)

        input_messages = context + [HumanMessage(content=input_text)]
        result = self._agent.invoke({"messages": input_messages})
        history.add_messages(result["messages"][len(context):])

        if self._injector.memory_compactor:
            self._injector.memory_compactor.compact_if_needed()

        return result["output"]
```
