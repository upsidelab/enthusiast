import logging

from enthusiast_common.injectors import BaseInjector
from enthusiast_common.tools import BaseLLMTool
from langchain_core.language_models import BaseLanguageModel
from langchain_core.prompts import PromptTemplate
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

from agent.repositories import DjangoDataSetRepository

logger = logging.getLogger(__name__)

VERIFY_DATA_PROMPT_TEMPLATE = """
You are verifying extracted data that describes a sofa.

{data}

Check if any **dimensions, quantities, or values are realistic for a single sofa.

Ignore minor deviations.
Flag only when the data is extremely unlikely to be true for a sofa.

Return:
Brief summary of anything that looks suspicious.
"""


class DataVerificationToolInput(BaseModel):
    data: str = Field(description="extracted data")
    product: str = Field(description="What type of product it is, specific")


class DataVerificationTool(BaseLLMTool):
    NAME = "data_verification_tool"
    DESCRIPTION = (
        "Always use this tool. Use this tool to verify if a data has expected shape and it's relevant to product type."
    )
    ARGS_SCHEMA = DataVerificationToolInput
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

    def run(self, data: str, product: str) -> StructuredTool:
        prompt = PromptTemplate.from_template(VERIFY_DATA_PROMPT_TEMPLATE)
        chain = prompt | self.llm

        llm_result = chain.invoke(
            {
                "data": data,
                "product": product,
            }
        )
        print(llm_result)
        return f"You received the following validation report {llm_result.content}. Respond with the product json, and if any field looks suspicious, add a field called <fieldname>_warning with description of the issue."

    def as_tool(self) -> StructuredTool:
        return StructuredTool.from_function(
            func=self.run,
            name=self.NAME,
            description=self.DESCRIPTION,
            args_schema=self.ARGS_SCHEMA,
            return_direct=self.RETURN_DIRECT,
        )
