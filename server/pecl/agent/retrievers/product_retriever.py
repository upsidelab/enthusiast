from django.core import serializers
from langchain_core.prompts import PromptTemplate

from agent.core import LlmProvider
from ecl.models import Product, DataSet

QUERY_PROMPT_TEMPLATE = """
    With the following database schema delimited by three backticks ```
    CREATE TABLE ecl_products (
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
    Respond with the where portion of the query only, don't include any other characters.
"""


class ProductRetriever:
    def __init__(self, data_set: DataSet, max_sample_products: int = 12):
        self.data_set = data_set
        self.max_sample_products = max_sample_products

    def find_products_matching_query(self, where_clause: str):
        where_clause = self._build_where_clause_for_query(where_clause)
        return Product.objects.raw("SELECT * FROM ecl_product " + where_clause + " AND company_code_id = %s limit 13",
                                   [self.data_set.id])

    def _get_sample_products_json(self):
        sample_products = Product.objects.filter(company_code_id__exact=self.data_set.id)[:self.max_sample_products]
        return serializers.serialize("json", sample_products)

    def _build_where_clause_for_query(self, query: str):
        chain = PromptTemplate.from_template(QUERY_PROMPT_TEMPLATE) | LlmProvider.provide_llm_instance()
        llm_result = chain.invoke({"sample_products_json": self._get_sample_products_json(), "query": query})
        sanitized_result = llm_result.content.strip("`").replace("%", "%%")
        return sanitized_result
