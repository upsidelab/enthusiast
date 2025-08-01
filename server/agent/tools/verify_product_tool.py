import logging

from enthusiast_common.injectors import BaseInjector
from enthusiast_common.tools import BaseLLMTool
from langchain_core.language_models import BaseLanguageModel
from langchain_core.prompts import PromptTemplate
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

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
    CONFIGURATION_ARGS = None

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

    def as_tool(self) -> StructuredTool:
        return StructuredTool.from_function(
            func=self.run,
            name=self.NAME,
            description=self.DESCRIPTION,
            args_schema=self.ARGS_SCHEMA,
            return_direct=self.RETURN_DIRECT,
        )
