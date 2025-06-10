import logging

import tiktoken
from enthusiast_common.injectors import BaseInjector
from enthusiast_common.tools import BaseLLMTool
from langchain_core.language_models import BaseLanguageModel
from langchain_core.prompts import PromptTemplate
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

from agent.repositories import DjangoDataSetRepository

logger = logging.getLogger(__name__)

LIMIT_PRODUCTS_PROMPT_TEMPLATE = """
You are helping a user choose a product. The current list of matching products is:

{products}

The user asked: "{user_query}"

Try to narrow down the list to one product.
If the question is too vague or you need more info to choose one product, ask a follow-up question.

Return your response in the following format:
- If narrowed list is sufficient: "RESULT: [...product descriptions...]"
- If more clarification is needed: "QUESTION: <follow-up question>"
"""


class LimitNumberOfProductsInput(BaseModel):
    full_user_request: str = Field(description="user's full request")
    products: str = Field(description="string containing list of products from products search")


class LimitNumberOfProductsTool(BaseLLMTool):
    NAME = "narrow_down_number_of_products"
    DESCRIPTION = "Use this tool with two arguments first is user_request and second a string containing a list of products. When you need to narrow down list of products"
    ARGS_SCHEMA = LimitNumberOfProductsInput
    RETURN_DIRECT = False

    ENCODING: tiktoken.encoding_for_model = None

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
        if llm.name in tiktoken.model.MODEL_TO_ENCODING:
            self.ENCODING = tiktoken.encoding_for_model(llm.name)
        else:
            self.ENCODING = tiktoken.encoding_for_model("gpt-4o")

    def run(self, full_user_request: str, products: str):
        prompt = PromptTemplate.from_template(LIMIT_PRODUCTS_PROMPT_TEMPLATE)
        chain = prompt | self.llm

        llm_result = chain.invoke(
            {
                "user_query": full_user_request,
                "products": products,
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
