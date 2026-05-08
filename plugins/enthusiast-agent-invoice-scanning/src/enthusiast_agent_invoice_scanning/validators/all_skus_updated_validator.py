from enthusiast_common.agentic_execution import (
    BaseExecutionValidator,
    ValidatorFailureResponse,
    ValidatorResponse,
    ValidatorSuccessResponse,
)
from enthusiast_common.agentic_execution.memory import ToolScratchpad

from enthusiast_agent_invoice_scanning.execution_input import InvoiceScanningAgenticExecutionInput
from enthusiast_agent_invoice_scanning.tools.update_stock_levels_tool import (
    StockUpdateMemoryEntry,
    UpdateStockLevelsTool,
)


class AllSkusUpdatedValidator(BaseExecutionValidator):
    """Ensures all SKUs provided in the execution input were processed by the stock update tool.

    When the input specifies a list of expected SKUs, this validator checks that every
    SKU was attempted. Missing SKUs trigger a retryable failure so the agent can search
    the invoice again and retry. If no SKUs are specified in the input, validation is skipped.
    """

    _TOOL_NAME = UpdateStockLevelsTool.NAME

    def validate(
        self,
        response: str,
        execution_input: InvoiceScanningAgenticExecutionInput,
        tool_scratchpad: ToolScratchpad,
    ) -> ValidatorResponse:
        if not execution_input.skus:
            return ValidatorSuccessResponse()

        attempted_skus: set[str] = set()
        entry: StockUpdateMemoryEntry | None = tool_scratchpad.read(self._TOOL_NAME)
        if entry:
            attempted_skus.update(entry.keys())

        missing_skus = [sku for sku in execution_input.skus if sku not in attempted_skus]
        if not missing_skus:
            return ValidatorSuccessResponse()

        skus_list = ", ".join(missing_skus)
        return ValidatorFailureResponse(
            feedback=(
                f"The following SKUs from the expected list were not updated: {skus_list}. "
                f"Re-read the invoice and look for these specific SKUs. "
                f"If they are present, call the stock update tool for all missing SKUs. "
                f"If they are not present in the invoice, stop the execution."
            ),
            retry_needed=True,
        )
