from enthusiast_agent_tool_calling import BaseToolCallingAgent
from enthusiast_common.config.base import LLMToolConfig
from enthusiast_common.utils import RequiredFieldsModel
from pydantic import Field, Json

from enthusiast_agent_catalog_enrichment.tools import UpsertProductDetailsTool

from .tools.scrape_product_tool import ScrapeProductTool

_CONFIRMATION_REQUIRED_INSTRUCTION = (
    "CONFIRMATION REQUIRED: Do NOT call the upsert tool without explicit user confirmation first. "
    "After fetching and extracting data from all URLs, present the extracted product data to the user "
    "in a clean, readable format: use the product name as a bold header, list each extracted field "
    "as a bullet point, and separate products with a horizontal rule (---). "
    "After listing all products, ask on a new line: 'Shall I upsert these products into the catalog?' "
    "Wait for the user to confirm before calling the upsert tool. "
    "If the user declines, do not upsert and ask what they would like to change."
)

_AUTO_CONFIRM_INSTRUCTION = (
    "Proceed with upserting products automatically after extraction — "
    "do not ask the user for confirmation before calling the upsert tool."
)


class ProductWebScraperPromptInput(RequiredFieldsModel):
    """Runtime configuration for the Product Web Scraper agent."""

    output_format: Json = Field(
        title="Output format",
        description="Output format of the extracted product data",
        default='{"sku": "string", "name": "string"}',
    )
    auto_confirm: bool = Field(
        title="Auto confirm upsert",
        description=(
            "When enabled, the agent upserts extracted products immediately without asking "
            "for confirmation. When disabled (default), the agent shows extracted data first "
            "and waits for explicit user approval before writing to the catalog."
        ),
        default=False,
    )


class ProductWebScraperAgent(BaseToolCallingAgent):
    """Agent that fetches product data from web pages and upserts it into the ecommerce catalog.

    The user provides one or more product page URLs. The agent fetches each page, extracts
    product fields according to the configured output format, optionally cross-checks data
    from multiple URLs describing the same product, then upserts all products in a single
    batch call.

    When auto_confirm is False (default), the agent presents extracted data to the user and
    waits for explicit confirmation before upserting. When True, it upserts immediately.
    """

    AGENT_KEY = "enthusiast-agent-product-web-scraper"
    NAME = "Product Web Scraper"
    PROMPT_INPUT = ProductWebScraperPromptInput
    FILE_UPLOAD = False
    TOOLS = [
        LLMToolConfig(tool_class=ScrapeProductTool),
        LLMToolConfig(tool_class=UpsertProductDetailsTool),
    ]

    def _get_system_prompt_variables(self) -> dict:
        upsert_instruction = (
            _AUTO_CONFIRM_INSTRUCTION
            if self.PROMPT_INPUT.auto_confirm
            else _CONFIRMATION_REQUIRED_INSTRUCTION
        )
        return {
            "data_format": self.PROMPT_INPUT.output_format,
            "upsert_confirmation_instruction": upsert_instruction,
        }
