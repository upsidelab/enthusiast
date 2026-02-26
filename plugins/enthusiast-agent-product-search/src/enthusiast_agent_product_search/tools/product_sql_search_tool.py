import json

from enthusiast_common.tools import BaseLLMTool
from enthusiast_common.errors import RetrieverError
from pydantic import BaseModel, Field


class ProductSearchInput(BaseModel):
    sql_query: str = Field(description="SQL SELECT query on catalog_product table. MUST include id in SELECT clause.")
    expected_results: int = Field(description="expected number of results, pass 1 if not provided")


class ProductSQLSearchTool(BaseLLMTool):
    NAME = "product_sql_search"
    DESCRIPTION = "useful for finding products matching provided description"
    ARGS_SCHEMA = ProductSearchInput
    RETURN_DIRECT = False

    def run(self, sql_query: str, expected_results: int):
        product_retriever = self._injector.product_retriever
        try:
            relevant_products = product_retriever.find_products_with_sql(sql_query)
        except RetrieverError as e:
            return e.agent_friendly_message

        if not relevant_products:
            return "No products found, try to loosen the criteria"

        serialized_products = product_retriever.product_details_as_json(relevant_products)
        serialized_products_json = json.dumps(serialized_products)

        if len(relevant_products) > expected_results:
            return f"Found {len(relevant_products)} products: {serialized_products_json}. Ask a follow up question about a single attribute, that will allow you to narrow down the results."

        return serialized_products_json
