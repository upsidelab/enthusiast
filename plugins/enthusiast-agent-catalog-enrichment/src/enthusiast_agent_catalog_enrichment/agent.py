from enthusiast_domain.builder import EcommerceAgentBuilder
from enthusiast_domain_tools import UpsertProductDetailsTool
from pydantic import Field, Json
from suvereo_agent_tool_calling import BaseToolCallingAgent
from suvereo_common.config.base import LLMToolConfig
from suvereo_common.utils import RequiredFieldsModel

from .prompt import CATALOG_ENRICHMENT_TOOL_CALLING_AGENT_PROMPT


class ExtractDataPromptInput(RequiredFieldsModel):
    output_format: Json = Field(title="Output format",
                                description="Output format of the extracted data",
                                default='{"sku": "string", "name": "string"}')


class CatalogEnrichmentAgent(BaseToolCallingAgent):
    AGENT_KEY = "enthusiast-agent-catalog-enrichment"
    NAME = "Catalog Enrichment"
    SYSTEM_PROMPT = CATALOG_ENRICHMENT_TOOL_CALLING_AGENT_PROMPT
    BUILDER_CLASS = EcommerceAgentBuilder
    PROMPT_INPUT = ExtractDataPromptInput
    FILE_UPLOAD = True
    TOOLS = [
        LLMToolConfig(tool_class=UpsertProductDetailsTool),
    ]

    def _get_system_prompt_variables(self) -> dict:
        return {"data_format": self.PROMPT_INPUT.output_format}
