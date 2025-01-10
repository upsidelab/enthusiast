from django.core import serializers
from langchain_core.prompts import PromptTemplate

from catalog.language_models import LanguageModelRegistry
from catalog.models import Product, DataSet

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


class ProductRetriever:
    def __init__(self, data_set: DataSet, number_of_products: int = 12, max_sample_products: int = 12):
        self.data_set = data_set
        self.number_of_products = number_of_products
        self.max_sample_products = max_sample_products

    def find_products_matching_query(self, user_query: str):
        agent_where_clause = self._build_where_clause_for_query(user_query)
        where_conditions = [f"data_set_id = {self.data_set.id}"]  # Security: access only to approved data set.
        if agent_where_clause:
            where_conditions.append(agent_where_clause)
        return Product.objects.extra(where=where_conditions)[:self.number_of_products]

    def _get_sample_products_json(self):
        sample_products = Product.objects.filter(data_set_id__exact=self.data_set.id)[:self.max_sample_products]
        return serializers.serialize("json", sample_products)

    def _build_where_clause_for_query(self, query: str):
        llm = LanguageModelRegistry().provider_for_dataset(self.data_set).provide_language_model()
        chain = PromptTemplate.from_template(QUERY_PROMPT_TEMPLATE) | llm
        llm_result = chain.invoke({"sample_products_json": self._get_sample_products_json(), "query": query})
        sanitized_result = llm_result.content.strip("`").removeprefix("sql").strip("\n").replace("%", "%%")
        return sanitized_result
