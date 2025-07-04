import logging

from django.core import serializers
from enthusiast_common.injectors import BaseInjector
from enthusiast_common.tools import BaseLLMTool
from langchain_core.language_models import BaseLanguageModel
from pydantic import BaseModel, Field

from agent.repositories import DjangoDataSetRepository
from catalog.models import Product

logger = logging.getLogger(__name__)


class AgentProductSearchToolInput(BaseModel):
    sql_query: str = Field(description="sql select query to execute on the catalog_product table. include both where and order clauses")


class AgentProductSearchTool(BaseLLMTool):
    NAME = "products_search_tool"
    DESCRIPTION = "use it for initial products fetch"
    ARGS_SCHEMA = AgentProductSearchToolInput
    RETURN_DIRECT = False

    def __init__(
        self,
        data_set_id: int,
        data_set_repo: DjangoDataSetRepository,
        llm: BaseLanguageModel,
        injector: BaseInjector | None,
    ):
        super().__init__(data_set_id=data_set_id, data_set_repo=data_set_repo, llm=llm, injector=injector)
        self.data_set_id = data_set_id
        self.data_set_repo = data_set_repo
        self.llm = llm
        self.injector = injector

    def run(self, sql_query: str):
        try:
            products = Product.objects.raw(sql_query)
            products = list(products)
        except Exception as e:
            logger.info(e)
            return f"The query you provided is incorrect Error: {type(e).__name__} - {e}. Fix your query and try again."

        if len(products) > 0:
            serialized_products = serializers.serialize("json", products)
            return f"Found the following products: {serialized_products}. Pick the one that matches the most and validate whether it's a good fit."
        else:
            return "No products were found, try loosening the criteria"