---
sidebar_position: 5
---

# Concept: Product search Agent
This example will walk you through a concept of a tool calling agent that searches for products and verifies results based on user's input. It will also cover more complex customizations.


## Creating an Agent
As usual, start by creating an agent directory, and then create:

### Prompt
Define the prompt as a plain string in `prompt.py`:
````python
PRODUCT_FINDER_AGENT_PROMPT = """
You are a helpful product search assistant.
Help the user find {products_type} products that match their criteria.
Always search for products first, then verify the results match the user's requirements.
If no products match, ask the user to refine their criteria.
"""
````

### Tools
Create two tools
1. Product Search Tool – responsible for retrieving products from the database.

```python
from typing import Any

from enthusiast_common.injectors import BaseInjector
from enthusiast_common.tools import BaseLLMTool
from langchain_core.language_models import BaseLanguageModel
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field


class ProductVectorStoreSearchInput(BaseModel):
    full_user_request: str = Field(description="user's full request")
    keyword: str = Field(
        description="one-word keyword which will determine an attribute of product for postgres search. It can be color, country, shape"
    )


class ProductVectorStoreSearchTool(BaseLLMTool):
    NAME = "search_matching_products"
    DESCRIPTION = (
        "It's tool for vector store search use it with suitable phrases when you need to find matching products"
    )
    ARGS_SCHEMA = ProductVectorStoreSearchInput
    RETURN_DIRECT = False

    def __init__(
        self,
        data_set_id: int,
        llm: BaseLanguageModel,
        injector: BaseInjector | None,
    ):
        super().__init__(data_set_id=data_set_id, llm=llm, injector=injector)
        self.data_set_id = data_set_id
        self.llm = llm
        self.injector = injector

    def run(self, full_user_request: str, keyword: str) -> list[Any]:
        product_retriever = self.injector.product_retriever
        relevant_products = product_retriever.find_content_matching_query(full_user_request, keyword)
        context = [product.content for product in relevant_products]
        return context


```
2. Product Verification Tool – verifies whether the retrieved products match the user’s criteria.
```python
from enthusiast_common.injectors import BaseInjector
from enthusiast_common.tools import BaseLLMTool
from langchain_core.language_models import BaseLanguageModel
from langchain_core.prompts import PromptTemplate
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

VERIFY_PRODUCT_PROMPT_TEMPLATE = """
Consider following product {product} it is a {products_type}.
Does it match the search criteria {search_criteria} in general, it doesn't have to be 100% match?
"""


class ProductVerificationToolInput(BaseModel):
    search_criteria: str = Field(description="Complete user's search criteria")
    product: str = Field(description="product data")
    products_type: str = Field(description="What type of product it is, specific")


class ProductVerificationTool(BaseLLMTool):
    NAME = "product_verification_tool"
    DESCRIPTION = "Always use this tool. Use this tool to verify if a product fulfills user criteria."
    ARGS_SCHEMA = ProductVerificationToolInput
    RETURN_DIRECT = False

    def __init__(
        self,
        data_set_id: int,
        llm: BaseLanguageModel,
        injector: BaseInjector | None,
    ):
        super().__init__(data_set_id=data_set_id, llm=llm, injector=injector)
        self.data_set_id = data_set_id
        self.llm = llm
        self.injector = injector

    def run(self, search_criteria: str, product: str, products_type: str) -> StructuredTool:
        prompt = PromptTemplate.from_template(VERIFY_PRODUCT_PROMPT_TEMPLATE)
        chain = prompt | self.llm

        llm_result = chain.invoke(
            {
                "search_criteria": search_criteria,
                "product": product,
                "products_type": products_type,
            }
        )
        return llm_result.content


```
### Agent
Define the agent class with its required class variables in `agent.py`:
```python
from enthusiast_agent_tool_calling import BaseToolCallingAgent
from enthusiast_common.config.base import LLMToolConfig
from enthusiast_common.utils import RequiredFieldsModel
from pydantic import Field

from .tools.product_search import ProductVectorStoreSearchTool
from .tools.product_verification import ProductVerificationTool


class ProductSearchPromptInput(RequiredFieldsModel):
    products_type: str = Field(title="Products type", description="Type of products to search for", default="any")


class ProductSearchAgent(BaseToolCallingAgent):
    AGENT_KEY = "enthusiast-agent-product-search-concept"
    NAME = "Product Search"
    PROMPT_INPUT = ProductSearchPromptInput
    TOOLS = [
        LLMToolConfig(tool_class=ProductVectorStoreSearchTool),
        LLMToolConfig(tool_class=ProductVerificationTool),
    ]

    def get_answer(self, input_text: str) -> str:
        agent_executor = self._build_agent_executor()
        agent_output = agent_executor.invoke(
            {"input": input_text, "products_type": self.PROMPT_INPUT.products_type},
            config=self._build_invoke_config(),
        )
        return agent_output["output"]


```

### Retriever
Let's create custom product vector store retriever
```python
from django.db.models import QuerySet
from enthusiast_common.config import AgentConfig
from enthusiast_common.registry import BaseEmbeddingProviderRegistry
from enthusiast_common.retrievers import BaseVectorStoreRetriever
from enthusiast_common.structures import RepositoriesInstances
from langchain_core.language_models import BaseLanguageModel
from pgvector.django import CosineDistance


class ProductVectorStoreRetriever(BaseVectorStoreRetriever):
    def find_content_matching_query(self, query: str, keyword: str = "") -> QuerySet:
        embedding_vector = self._create_embedding_for_query(query)
        relevant_products = self._find_products_matching_vector(embedding_vector, keyword)
        return relevant_products

    def _create_embedding_for_query(self, query: str) -> list[float]:
        data_set = self.data_set_repo.get_by_id(self.data_set_id)
        embedding_provider = self.embeddings_registry.provider_for_dataset(self.data_set_id)
        return embedding_provider(data_set.embedding_model, data_set.embedding_vector_dimensions).generate_embeddings(
            query
        )

    def _find_products_matching_vector(
        self, embedding_vector: list[float], keyword: str
    ) -> QuerySet:
        embedding_distance = CosineDistance("embedding", embedding_vector)
        embeddings_with_products = self.model_chunk_repo.get_chunk_by_distance_and_keyword_for_data_set(
            self.data_set_id, embedding_distance, keyword
        )
        limited_embeddings_with_products = embeddings_with_products[: self.max_objects]
        return limited_embeddings_with_products

    @classmethod
    def create(
        cls,
        config: AgentConfig,
        data_set_id: int,
        repositories: RepositoriesInstances,
        embeddings_registry: BaseEmbeddingProviderRegistry,
        llm: BaseLanguageModel,
    ) -> BaseVectorStoreRetriever:
        return cls(
            data_set_id=data_set_id,
            data_set_repo=repositories.data_set,
            model_chunk_repo=repositories.product_chunk,
            embeddings_registry=embeddings_registry,
            **config.retrievers.product.extra_kwargs,
        )



class DocumentRetriever(BaseVectorStoreRetriever):
    def find_content_matching_query(self, query: str) -> QuerySet:
        embedding_vector = self._create_embedding_for_query(query)
        relevant_documents = self._find_documents_matching_vector(embedding_vector)
        return relevant_documents

    def _create_embedding_for_query(self, query: str) -> list[float]:
        data_set = self.data_set_repo.get_by_id(self.data_set_id)
        embedding_provider = self.embeddings_registry.provider_for_dataset(self.data_set_id)
        return embedding_provider(data_set.embedding_model, data_set.embedding_vector_dimensions).generate_embeddings(
            query
        )

    def _find_documents_matching_vector(self, embedding_vector: list[float]) -> QuerySet:
        embedding_distance = CosineDistance("embedding", embedding_vector)
        embeddings_with_documents = self.model_chunk_repo.get_chunk_by_distance_for_data_set(
            self.data_set_id, embedding_distance
        )
        limited_embeddings_with_documents = embeddings_with_documents[: self.max_objects]
        return limited_embeddings_with_documents

    @classmethod
    def create(
        cls,
        config: AgentConfig,
        data_set_id: int,
        repositories: RepositoriesInstances,
        embeddings_registry: BaseEmbeddingProviderRegistry,
        llm: BaseLanguageModel,
    ) -> BaseVectorStoreRetriever:
        return cls(
            data_set_id=data_set_id,
            data_set_repo=repositories.data_set,
            model_chunk_repo=repositories.document_chunk,
            embeddings_registry=embeddings_registry,
            **config.retrievers.document.extra_kwargs,
        )


```
### Memory

```python
import typing
from abc import ABC
from typing import Dict, Any

from langchain.memory import ConversationBufferMemory, ConversationTokenBufferMemory, ConversationSummaryBufferMemory
from langchain_core.messages import AIMessage, FunctionMessage, HumanMessage

from enthusiast_common.repositories import BaseConversationRepository
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage, messages_from_dict


class PersistentChatHistory(BaseChatMessageHistory):
    """
    A chat history implementation that persists messages in the database.
    Inject it to agent's memory, to enable conversation persistence.
    """

    def __init__(self, conversation_repo: BaseConversationRepository, conversation_id: Any):
        self._conversation = conversation_repo.get_by_id(conversation_id)

    def add_message(self, message: BaseMessage) -> None:
        self._conversation.messages.create(role=message.type, text=message.content)

    @property
    def messages(self) -> list[BaseMessage]:
        messages = self._conversation.messages.filter(answer_failed=False).order_by("created_at")
        message_dicts = [{"type": message.role, "data": {"content": message.text}} for message in messages]
        return messages_from_dict(message_dicts)

    def clear(self) -> None:
        self._conversation.messages.all().delete()


class PersistIntermediateStepsMixin(ABC):
    """
    This mixin can be added to a ConversationBufferMemory class in order to persist agent's function calls.
    """

    def save_context(self, inputs: Dict[str, Any], outputs: Dict[str, str]) -> None:
        self_as_conversation_memory = typing.cast(ConversationBufferMemory, self)

        human_message = HumanMessage(inputs["input"])
        self_as_conversation_memory.chat_memory.add_message(human_message)

        if "intermediate_steps" in outputs:
            for agent_action, result in outputs["intermediate_steps"]:
                self_as_conversation_memory.chat_memory.add_message(agent_action.messages[0])

                function_message = FunctionMessage(name=agent_action.tool, content=result)
                self_as_conversation_memory.chat_memory.add_message(function_message)

        ai_message = AIMessage(outputs["output"])
        self_as_conversation_memory.chat_memory.add_message(ai_message)



class LimitedChatMemory(PersistIntermediateStepsMixin, ConversationTokenBufferMemory):
    """
    This memory persists intermediate steps, and limits the amount of tokens passed back to the agent to
    what's defined as max_token_limit.
    """

    pass


class SummaryChatMemory(PersistIntermediateStepsMixin, ConversationSummaryBufferMemory):
    """
    This memory persists intermediate steps, and summarizes the history passed back to the agent if the history
    exceeds the token limit.
    """

    pass
```

### Builder
```python
from typing import Optional

from enthusiast_common.agents import BaseAgent
from enthusiast_common.builder import BaseAgentBuilder, RepositoriesInstances
from enthusiast_common.config import AgentConfig, LLMConfig
from enthusiast_common.injectors import BaseInjector
from enthusiast_common.registry import BaseDBModelsRegistry, BaseEmbeddingProviderRegistry, BaseLanguageModelRegistry
from enthusiast_common.retrievers import BaseVectorStoreRetriever
from enthusiast_common.tools import BaseAgentTool, BaseFunctionTool, BaseLLMTool
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.language_models import BaseLanguageModel
from langchain_core.prompts import ChatMessagePromptTemplate, PromptTemplate
from langchain_core.tools import BaseTool

from .memory import PersistentChatHistory, SummaryChatMemory, LimitedChatMemory


class AgentBuilder(BaseAgentBuilder[AgentConfig]):
    def _build_agent(
        self,
        tools: list[BaseTool],
        llm: BaseLanguageModel,
        prompt: PromptTemplate | ChatMessagePromptTemplate,
        callback_handler: BaseCallbackHandler,
    ) -> BaseAgent:
        return self._config.agent_class(
            tools=tools,
            llm=llm,
            prompt=prompt,
            conversation_id=self._config.conversation_id,
            callback_handler=callback_handler,
            injector=self._injector,
        )

    def _build_llm_registry(self) -> BaseLanguageModelRegistry:
        llm_registry_class = self._config.registry.llm.registry_class
        data_set_repo = self._repositories.data_set
        if providers := self._config.registry.llm.providers:
            llm_registry = llm_registry_class(providers=providers)
        else:
            llm_registry = llm_registry_class(data_set_repo=data_set_repo)
        return llm_registry

    def _build_db_models_registry(self) -> BaseDBModelsRegistry:
        db_models_registry_class = self._config.registry.model.registry_class
        if models_config := self._config.registry.model.models_config:
            db_model_registry = db_models_registry_class(models_config=models_config)
        else:
            db_model_registry = db_models_registry_class()
        return db_model_registry

    def _build_and_set_repositories(self, models_registry: BaseDBModelsRegistry) -> None:
        repositories = {}
        for name in self._config.repositories.__class__.model_fields.keys():
            repo_class = getattr(self._config.repositories, name)
            model_class = models_registry.get_model_class_by_name(name)
            repositories[name] = repo_class(model_class)
        self._repositories = RepositoriesInstances(**repositories)

    def _build_embeddings_registry(self) -> BaseEmbeddingProviderRegistry:
        embeddings_registry_class = self._config.registry.embeddings.registry_class
        data_set_repo = self._repositories.data_set
        if providers := self._config.registry.llm.providers:
            embeddings_registry = embeddings_registry_class(providers=providers)
        else:
            embeddings_registry = embeddings_registry_class(data_set_repo=data_set_repo)
        return embeddings_registry

    def _build_llm(self, llm_config: LLMConfig) -> BaseLanguageModel:
        data_set_repo = self._repositories.data_set
        llm_registry = self._build_llm_registry()
        llm = self._config.llm.llm_class(
            llm_registry=llm_registry,
            callbacks=llm_config.callbacks,
            streaming=llm_config.streaming,
            data_set_repo=data_set_repo,
        )
        return llm.create(self._data_set_id)

    def _build_default_llm(self) -> BaseLanguageModel:
        llm_registry_class = self._config.registry.llm.registry_class
        data_set_repo = self._repositories.data_set
        if providers := self._config.registry.llm.providers:
            llm_registry = llm_registry_class(providers=providers)
        else:
            llm_registry = llm_registry_class(data_set_repo=data_set_repo)

        llm = self._config.llm.llm_class(
            llm_registry=llm_registry,
            data_set_repo=data_set_repo,
        )
        return llm.create(self._data_set_id)

    def _build_tools(self, default_llm: BaseLanguageModel, injector: BaseInjector) -> list[BaseTool]:
        function_tools = self._build_function_tools() if self._config.function_tools else []
        llm_tools = self._build_llm_tools(default_llm, injector) if self._config.llm_tools else []
        agent_tools = self._build_agent_tools() if self._config.agent_tools else []
        return [*function_tools, *llm_tools, *agent_tools]

    def _build_function_tools(self) -> list[BaseFunctionTool]:
        return [tool() for tool in self._config.function_tools]

    def _build_llm_tools(self, default_llm: BaseLanguageModel, injector: BaseInjector) -> list[BaseLLMTool]:
        tools = []
        for tool_config in self._config.llm_tools:
            llm = default_llm
            data_set_id = tool_config.data_set_id or self._data_set_id
            if tool_config.llm:
                llm = tool_config.llm
            tools.append(
                tool_config.tool_class(
                    data_set_id=data_set_id,
                    llm=llm,
                    injector=injector,
                )
            )
        return tools

    def _build_agent_tools(self) -> list[BaseAgentTool]:
        return [tool_config.tool_class(agent=tool_config.agent) for tool_config in self._config.agent_tools]

    def _build_injector(self) -> BaseInjector:
        document_retriever = self._build_document_retriever()
        product_retriever = self._build_product_retriever()
        return self._config.injector(
            product_retriever=product_retriever,
            document_retriever=document_retriever,
            repositories=self._repositories,
            chat_summary_memory=self._chat_summary_memory,
            chat_limited_memory=self._chat_limited_memory,
        )

    def _build_agent_callback_handler(self) -> Optional[BaseCallbackHandler]:
        if self._config.agent_callback_handler:
            return self._config.agent_callback_handler.handler_class(**self._config.agent_callback_handler.args)
        return None

    def _build_product_retriever(self) -> BaseVectorStoreRetriever:
        return self._config.retrievers.product.retriever_class.create(
            config=self._config,
            data_set_id=self._data_set_id,
            repositories=self._repositories,
            embeddings_registry=self._embeddings_registry,
            llm=self._llm,
        )

    def _build_document_retriever(self) -> BaseVectorStoreRetriever:
        return self._config.retrievers.document.retriever_class.create(
            config=self._config,
            data_set_id=self._data_set_id,
            repositories=self._repositories,
            embeddings_registry=self._embeddings_registry,
            llm=self._llm,
        )

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

### Configuration
Create configuration inside `config.py` file:
```python
from enthusiast_common.config import AgentConfigWithDefaults
from enthusiast_common.config.base import RetrieverConfig, RetrieversConfig
from enthusiast_common.config.prompts import ChatPromptTemplateConfig, Message, MessageRole

from .agent import ProductSearchAgent
from .prompt import PRODUCT_FINDER_AGENT_PROMPT
from .retrievers import ProductVectorStoreRetriever, DocumentRetriever


def get_config() -> AgentConfigWithDefaults:
    return AgentConfigWithDefaults(
        prompt_template=ChatPromptTemplateConfig(
            messages=[
                Message(
                    role=MessageRole.SYSTEM,
                    content=PRODUCT_FINDER_AGENT_PROMPT,
                ),
                Message(role=MessageRole.PLACEHOLDER, content="{chat_history}"),
                Message(role=MessageRole.USER, content="{input}"),
                Message(role=MessageRole.PLACEHOLDER, content="{agent_scratchpad}"),
            ]
        ),
        agent_class=ProductSearchAgent,
        tools=ProductSearchAgent.TOOLS,
        retrievers=RetrieversConfig(
            document=RetrieverConfig(retriever_class=DocumentRetriever),
            product=RetrieverConfig(retriever_class=ProductVectorStoreRetriever, extra_kwargs={"max_objects": 30}),
        ),
    )

```
Finally add your agent to `settings_override.py`:
```python
AVAILABLE_AGENTS = [
    "enthusiast_custom.examples.product_search.product_search",
]

```
Now use product source plugin to load your products into DB.

