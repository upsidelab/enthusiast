import logging

import tiktoken
from django.core import serializers
from enthusiast_common.injectors import BaseInjector
from enthusiast_common.tools import BaseLLMTool
from langchain_core.language_models import BaseLanguageModel
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class ProductsSearchInput(BaseModel):
    full_user_request: str = Field(description="user's full request")


class ProductsSearchTool(BaseLLMTool):
    NAME = "products_search_tool"
    DESCRIPTION = "use it for initial products fetch"
    ARGS_SCHEMA = ProductsSearchInput
    RETURN_DIRECT = False
    CONFIGURATION_ARGS = None

    ENCODING: tiktoken.encoding_for_model = None

    def __init__(
        self,
        data_set_id: int,
        llm: BaseLanguageModel,
        injector: BaseInjector,
    ):
        super().__init__(data_set_id=data_set_id, llm=llm, injector=injector)
        self.data_set_id = data_set_id
        self.llm = llm
        self.injector = injector
        if llm.name in tiktoken.model.MODEL_TO_ENCODING:
            self.ENCODING = tiktoken.encoding_for_model(llm.name)
        else:
            self.ENCODING = tiktoken.encoding_for_model("gpt-4o")

    def run(self, full_user_request: str):
        product_retriever = self.injector.product_retriever
        relevant_products = product_retriever.find_products_matching_query(full_user_request)

        product_context = serializers.serialize("json", relevant_products)
        return product_context
