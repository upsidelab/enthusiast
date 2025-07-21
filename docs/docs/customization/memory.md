---
sidebar_position: 7
---

# Agent's memory

## Default memory
By default, Enthusiast provides two types of agent's memory classes.
1. `LimitedChatMemory`(extension of `ConversationTokenBufferMemory`) - 

2. `SummaryChatMemory` (extension of `ConversationSummaryBufferMemory`)

`LimitedChatMemory` keeps a rolling window of the most recent messages, measured by token count, and simply discards older ones when the limit is reached.

In contrast, `SummaryChatMemory` maintains a high‑level summary of older messages and combines it with a short buffer of recent raw messages, allowing the agent to preserve long‑term context without exceeding token limits.

In short, the first is ideal for short interactions where exact recent phrasing matters, while the second scales better for longer conversations by retaining summarized context over time.

Those two are accessible vie `_injector` inside Agent's class.
Example:
```python
    def _create_agent_executor(self, **kwargs):
        tools = self._create_tools()
        agent = create_tool_calling_agent(self._llm, tools, self._prompt)
        return AgentExecutor(
            agent=agent, tools=tools, verbose=True, memory=self._injector.chat_summary_memory, **kwargs
        )
```

## Customization
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

Build custom Injector based on enthusiast-common interface - `BaseInjector`:
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