from enthusiast_agent_tool_calling import BaseToolCallingAgent
from enthusiast_common.config.base import LLMToolConfig
from enthusiast_common.utils import RequiredFieldsModel
from pydantic import Field, Json

from .tools import UpsertProductDetailsTool


class ExtractDataPromptInput(RequiredFieldsModel):
    output_format: Json = Field(title="Output format",
                                description="Output format of the extracted data",
                                default='{"sku": "string", "name": "string"}')


class CatalogEnrichmentAgent(BaseToolCallingAgent):
    AGENT_KEY = "enthusiast-agent-catalog-enrichment"
    NAME = "Catalog Enrichment"
    PROMPT_INPUT = ExtractDataPromptInput
    FILE_UPLOAD = True
    TOOLS = [
        LLMToolConfig(tool_class=UpsertProductDetailsTool),
    ]

    def _get_system_prompt_variables(self) -> dict:
        return {"data_format": self.PROMPT_INPUT.output_format}
