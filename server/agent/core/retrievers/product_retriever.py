from typing import Self

import django
from django.core import serializers
from django.forms import model_to_dict
from enthusiast_common.builder import RepositoriesInstances
from enthusiast_common.config import AgentConfig
from enthusiast_common.registry import BaseEmbeddingProviderRegistry
from enthusiast_common.repositories import BaseDataSetRepository, BaseProductRepository
from enthusiast_common.retrievers import BaseProductRetriever
from langchain_core.language_models import BaseLanguageModel
from langchain_core.prompts import PromptTemplate

from agent.core.retrievers.retriever_sql_execution_error import RetrieverSQLExecutionError
from agent.core.retrievers.sql_validator import SQLValidator
from catalog.models import Product

QUERY_PROMPT_TEMPLATE = """
    With the following database schema delimited by three backticks ```
    CREATE TABLE catalog_product (
        \"id\" int8 NOT NULL,
        \"entry_id\" varchar NOT NULL,
        \"name\" varchar NOT NULL,
        \"slug\" varchar NOT NULL,
        \"description\" text NOT NULL,
        \"sku\" varchar NOT NULL,
        \"properties\" varchar NOT NULL,
        \"categories\" varchar NOT NULL,
        \"price\" float8 NOT NULL,
        PRIMARY KEY (\"id\")
    );```
    that contains product information, with some example values delimited by three backticks
    ```
    {sample_products_json}
    ```
    generate a where clause for an SQL query for fetching products that can be useful when answering the following 
    request delimited by three backticks.
    Make sure that the queries are case insensitive 
    ``` 
    {query} 
    ```
    Respond with the where portion of the query only, don't include any other characters, 
    skip initial where keyword, skip order by clause.
"""


class ProductRetriever(BaseProductRetriever):
    def __init__(
        self,
        data_set_id: int,
        data_set_repo: BaseDataSetRepository,
        product_repo: BaseProductRepository,
        llm: BaseLanguageModel,
        prompt_template: str,
        number_of_products: int = 12,
        max_sample_products: int = 12,
    ):
        self.data_set_id = data_set_id
        self.data_set_repo = data_set_repo
        self.product_repo = product_repo
        self.number_of_products = number_of_products
        self.max_sample_products = max_sample_products
        self.prompt_template = prompt_template
        self.llm = llm
        self._sql_validator = SQLValidator(allowed_table_name="catalog_product", data_set_id=self.data_set_id)

    def find_products_matching_query(self, user_query: str) -> list[Product]:
        agent_where_clause = self._build_where_clause_for_query(user_query)
        where_conditions = [f"data_set_id = {self.data_set_id}"]
        if agent_where_clause:
            where_conditions.append(agent_where_clause)

        return self.product_repo.extra(where_conditions=where_conditions)[: self.number_of_products]

    def _build_where_clause_for_query(self, query: str) -> str:
        chain = PromptTemplate.from_template(self.prompt_template) | self.llm
        llm_result = chain.invoke({"sample_products_json": self.get_sample_products_json(), "query": query})
        sanitized_result = llm_result.content.strip("`").removeprefix("sql").strip("\n").replace("%", "%%")
        return sanitized_result

    def find_products_with_sql(self, sql_query: str) -> list[Product]:
        sanitized_query = self._sql_validator.add_data_set_id_condition_and_raise_if_not_allowed(sql_query)
        cleaned_query = sanitized_query.replace("%", "%%")
        try:
            return list(Product.objects.raw(cleaned_query))
        except django.db.utils.ProgrammingError as e:
            raise RetrieverSQLExecutionError(e)

    def get_sample_products(self, num_sample_products: int = 12) -> list[Product]:
        sample_products = self.product_repo.filter(data_set_id=self.data_set_id)[: num_sample_products]
        return list(sample_products)

    def get_sample_products_json(self) -> str:
        return serializers.serialize("json", self.get_sample_products())

    def product_details_as_json(self, products: list[Product]) -> list[dict]:
        return [model_to_dict(product) for product in products]

    @classmethod
    def create(
        cls,
        config: AgentConfig,
        data_set_id: int,
        repositories: RepositoriesInstances,
        embeddings_registry: BaseEmbeddingProviderRegistry,
        llm: BaseLanguageModel,
    ) -> Self:
        return cls(
            data_set_id=data_set_id,
            data_set_repo=repositories.data_set,
            product_repo=repositories.product,
            llm=llm,
            **config.retrievers.product.extra_kwargs,
        )
