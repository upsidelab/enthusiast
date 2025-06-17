from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Iterable, Any

from langchain_core.language_models import BaseLanguageModel

from ..repositories import BaseProductRepository, BaseDataSetRepository

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

T = TypeVar("T")


class BaseProductRetriever(ABC, Generic[T]):
    def __init__(
        self,
        data_set_id: int,
        data_set_repo: BaseDataSetRepository,
        product_repo: BaseProductRepository,
        llm: BaseLanguageModel,
        prompt_template: str = QUERY_PROMPT_TEMPLATE,
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

    @abstractmethod
    def find_products_matching_query(self, user_query: str) -> Iterable[T]:
        pass

    def _get_sample_products_json(self) -> Any:
        pass

    def _build_where_clause_for_query(self, query: str) -> str:
        pass
