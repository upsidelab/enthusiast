from django.core import serializers
from enthusiast_common.injectors import BaseInjector
from enthusiast_common.tools import BaseLLMTool
from langchain_core.language_models import BaseLanguageModel
from pydantic import BaseModel, Field


class ProductSearchInput(BaseModel):
    product_description: str = Field(description="Product description to search for.")


class ProductSearchTool(BaseLLMTool):
    NAME = "search_matching_products"
    DESCRIPTION = "It's tool for DB search use it with suitable phrases when you need to find matching products"
    ARGS_SCHEMA = ProductSearchInput
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

    def run(self, product_description: str):
        product_retriever = self.injector.product_retriever
        relevant_products = product_retriever.find_products_matching_query(product_description)
        if not relevant_products:
            return "No products found, try to loosen the criteria"

        return serializers.serialize("json", relevant_products)
