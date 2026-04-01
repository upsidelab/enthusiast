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

    def _get_system_prompt_variables(self) -> dict:
        return {"products_type": self.PROMPT_INPUT.products_type}


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
### Configuration
Create configuration inside `config.py` file:
```python
from enthusiast_common.config import AgentConfigWithDefaults
from enthusiast_common.config.base import RetrieverConfig, RetrieversConfig

from .agent import ProductSearchAgent
from .prompt import PRODUCT_FINDER_AGENT_PROMPT
from .retrievers import ProductVectorStoreRetriever, DocumentRetriever


def get_config() -> AgentConfigWithDefaults:
    return AgentConfigWithDefaults(
        system_prompt=PRODUCT_FINDER_AGENT_PROMPT,
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

