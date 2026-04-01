---
sidebar_position: 3
---

# Memory

Enthusiast manages conversation memory through two complementary mechanisms: persistent storage to the database and token-limited context trimming before each agent invocation.

## Overview

Memory in Enthusiast serves two main purposes:
1. **Conversation Persistence**: Storing and retrieving the full chat history from the database
2. **Context Management**: Trimming history to a token budget before passing it to the LLM

## PersistentChatHistory

`PersistentChatHistory` implements `BaseChatMessageHistory` and is responsible for reading and writing messages to the database. It is injected into the agent via the `Injector` through the `chat_history` property.

```python
class PersistentChatHistory(BaseChatMessageHistory):
    def __init__(self, conversation_repo: BaseConversationRepository, conversation_id: Any):
        self._conversation = conversation_repo.get_by_id(conversation_id)

    def add_message(self, message: BaseMessage) -> None:
        ...

    @property
    def messages(self) -> list[BaseMessage]:
        ...
```

Messages are persisted after each agent turn by calling `history.add_messages(new_messages)`, where `new_messages` contains the full turn: human input, intermediate tool call/result pairs, and the final AI response.

## Token Limiting

Before each invocation, conversation history is trimmed using `trim_messages` from `langchain_core.messages`. The default token limit is 3000.

```python
from langchain_core.messages import trim_messages, HumanMessage

limited_history = trim_messages(
    history.messages,
    strategy="last",
    token_counter=llm,
    max_tokens=3000,
    start_on=HumanMessage,
    include_system=True,
    allow_partial=False,
)
```

This is handled automatically inside `BaseToolCallingAgent` — no manual configuration is required.

## Accessing Chat History

The chat history is accessible inside agents and tools via the injector:

```python
class MyAgent(BaseToolCallingAgent):
    def get_answer(self, input_text: str) -> str:
        history = self._injector.chat_history
        # history.messages → full conversation history
        # history.add_messages([...]) → persist new messages
```

## Extending the Injector with Additional State

If you need to persist additional state beyond conversation messages, extend `BaseInjector` with a custom property backed by its own repository or service:

```python
class CustomInjector(BaseInjector):
    def __init__(self, ..., custom_store: CustomStore):
        super().__init__(...)
        self._custom_store = custom_store

    @property
    def custom_store(self) -> CustomStore:
        return self._custom_store
```
