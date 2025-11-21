from enthusiast_agent_tool_calling import BaseToolCallingAgent
from enthusiast_common.config import LLMToolConfig
from enthusiast_common.utils import RequiredFieldsModel
from pydantic import Field, Json

from ..tools.extract_website_data import ExtractWebsiteDataTool


class CompetitorResearchToolCallingAgentPromptInput(RequiredFieldsModel):
    output_format: Json = Field(title="Output format", description="Output format of the extracted data")


class CompetitorResearchToolCallingAgent(BaseToolCallingAgent):
    PROMPT_INPUT = CompetitorResearchToolCallingAgentPromptInput
    TOOLS = [LLMToolConfig(tool_class=ExtractWebsiteDataTool)]

    def get_answer(self, input_text: str) -> str:
        agent_executor = self._build_agent_executor()
        agent_output = agent_executor.invoke(
            {"input": input_text, "data_format": self.PROMPT_INPUT.output_format}, config=self._build_invoke_config()
        )
        return agent_output["output"]
