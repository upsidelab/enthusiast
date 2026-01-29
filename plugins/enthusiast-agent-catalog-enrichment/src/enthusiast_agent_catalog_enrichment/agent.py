from enthusiast_agent_tool_calling import BaseToolCallingAgent
from enthusiast_common.utils import RequiredFieldsModel
from enthusiast_common.config.base import LLMToolConfig
from .tools.update_product_properties_tool import UpdateProductPropertiesTool
from pydantic import Field, Json


class ExtractDataPromptInput(RequiredFieldsModel):
    output_format: Json = Field(title="Output format",
                                description="Output format of the extracted data",
                                default='{"sku": "string", "name": "string"}')


class CatalogEnrichmentToolCallingAgent(BaseToolCallingAgent):
    PROMPT_INPUT = ExtractDataPromptInput
    FILE_UPLOAD = True
    TOOLS = [
        LLMToolConfig(tool_class=UpdateProductPropertiesTool),
    ]

    def get_answer(self, input_text: str) -> str:
        agent_executor = self._build_agent_executor()
        agent_output = agent_executor.invoke(
            {"input": input_text, "data_format": self.PROMPT_INPUT.output_format}, config=self._build_invoke_config()
        )
        return agent_output["output"]
