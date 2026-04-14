from enthusiast_agent_tool_calling import BaseToolCallingAgent
from enthusiast_common.config.base import LLMToolConfig
from enthusiast_common.utils import RequiredFieldsModel
from pydantic import Field, Json

from .tools.fetch_and_extract_product_data_tool import FetchAndExtractProductDataTool
from .tools.upsert_product_details_tool import UpsertProductDetailsTool


class ProductWebScraperPromptInput(RequiredFieldsModel):
    """Runtime configuration for the Product Web Scraper agent."""

    output_format: Json = Field(
        title="Output format",
        description="Output format of the extracted product data",
        default='{"sku": "string", "name": "string"}',
    )


class ProductWebScraperAgent(BaseToolCallingAgent):
    """Agent that fetches product data from web pages and upserts it into the ecommerce catalog.

    The user provides one or more product page URLs. The agent fetches each page, extracts
    product fields according to the configured output format, optionally cross-checks data
    from multiple URLs describing the same product, then upserts all products in a single
    batch call.
    """

    AGENT_KEY = "enthusiast-agent-product-web-scraper"
    NAME = "Product Web Scraper"
    PROMPT_INPUT = ProductWebScraperPromptInput
    FILE_UPLOAD = False
    TOOLS = [
        LLMToolConfig(tool_class=FetchAndExtractProductDataTool),
        LLMToolConfig(tool_class=UpsertProductDetailsTool),
    ]

    def _get_system_prompt_variables(self) -> dict:
        return {"data_format": self.PROMPT_INPUT.output_format}
