from enthusiast_agent_tool_calling import BaseToolCallingAgent
from enthusiast_common.config.base import LLMToolConfig
from enthusiast_common.utils import RequiredFieldsModel
from pydantic import Field, Json

from .tools.update_stock_levels_tool import UpdateStockLevelsTool

_CONFIRMATION_REQUIRED_INSTRUCTION = (
    "CONFIRMATION REQUIRED: Do NOT call the stock update tool without explicit user confirmation first. "
    "After extracting all line items from the invoice, present them to the user in a clean, readable format: "
    "use the SKU as a bold header, list the quantity as a bullet point, and separate items with a horizontal "
    "rule (---). After listing all items, ask on a new line: "
    "'Shall I update stock levels for these items?' "
    "Wait for the user to confirm before calling the stock update tool. "
    "If the user declines, do not update and ask what they would like to change."
)

_AUTO_CONFIRM_INSTRUCTION = (
    "Proceed with updating stock levels automatically after extraction — "
    "do not ask the user for confirmation before calling the stock update tool."
)


class InvoiceScanningPromptInput(RequiredFieldsModel):
    """Runtime configuration for the Invoice Scanning agent."""

    output_format: Json = Field(
        title="Output format",
        description="Output format of the extracted invoice line items",
        default='{"sku": "string", "quantity": "number"}',
    )
    auto_confirm: bool = Field(
        title="Auto confirm stock update",
        description="Skip confirmation and update stock immediately after extraction.",
        default=False,
    )


class InvoiceScanningAgent(BaseToolCallingAgent):
    """Agent that scans supplier invoices and updates stock levels in the ecommerce platform.

    The user uploads an invoice file. The agent extracts SKU and quantity data from each line
    item, validates the SKUs against the catalog, then updates stock levels in a single batch call.

    When auto_confirm is False (default), the agent presents extracted line items to the user
    and waits for explicit confirmation before updating. When True, it updates immediately.
    """

    AGENT_KEY = "enthusiast-agent-invoice-scanning"
    NAME = "Invoice Scanning"
    PROMPT_INPUT = InvoiceScanningPromptInput
    FILE_UPLOAD = True
    TOOLS = [
        LLMToolConfig(tool_class=UpdateStockLevelsTool),
    ]

    def _get_system_prompt_variables(self) -> dict:
        stock_update_instruction = (
            _AUTO_CONFIRM_INSTRUCTION
            if self.PROMPT_INPUT.auto_confirm
            else _CONFIRMATION_REQUIRED_INSTRUCTION
        )
        return {
            "data_format": self.PROMPT_INPUT.output_format,
            "stock_update_confirmation_instruction": stock_update_instruction,
        }
