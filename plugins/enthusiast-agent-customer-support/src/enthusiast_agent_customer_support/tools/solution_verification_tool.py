import logging

from enthusiast_common.tools import BaseLLMTool
from langchain_core.prompts import PromptTemplate
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

VERIFY_DATA_PROMPT_TEMPLATE = """
You are verifying solution for user_query based on user manual.


Given the following:
solution: {solution}
manuals: {manuals}
user_query: {user_query}

Check if all steps are relevant to manuals.
Return:
Brief explanation of any step that looks wrong.
"""


class SolutionVerificationToolInput(BaseModel):
    user_query: str = Field(description="User question or problem.")
    solution: str = Field(description="Your prepared solution.")
    manuals: str = Field(description="Relevant pieces of information from manuals.")


class SolutionVerificationTool(BaseLLMTool):
    NAME = "data_verification_tool"
    DESCRIPTION = (
        "Always use this tool. Use this tool to verify if a data has expected shape and it's relevant to product type."
    )
    ARGS_SCHEMA = SolutionVerificationToolInput
    RETURN_DIRECT = False

    def run(self, user_query: str, solution: str, manuals: str) -> StructuredTool:
        prompt = PromptTemplate.from_template(VERIFY_DATA_PROMPT_TEMPLATE)
        chain = prompt | self._llm

        llm_result = chain.invoke(
            {
                "user_query": user_query,
                "solution": solution,
                "manuals": manuals,
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
