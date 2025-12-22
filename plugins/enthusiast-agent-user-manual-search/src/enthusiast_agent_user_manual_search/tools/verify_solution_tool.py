from enthusiast_common.tools import BaseLLMTool
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field

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


class VerifySolutionToolInput(BaseModel):
    user_query: str = Field(description="User question or problem.")
    solution: str = Field(description="Your prepared solution.")
    manuals: str = Field(description="Relevant pieces of information from manuals.")


class VerifySolutionTool(BaseLLMTool):
    NAME = "verify_solution"
    DESCRIPTION = (
        "Always use this tool. Use this tool to verify if a data has expected shape and it's relevant to product type."
    )
    ARGS_SCHEMA = VerifySolutionToolInput
    RETURN_DIRECT = False

    def run(self, user_query: str, solution: str, manuals: str) -> str:
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
