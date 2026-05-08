from enthusiast_common.agentic_execution import (
    BaseExecutionValidator,
    ExecutionInputType,
    ValidatorFailureResponse,
    ValidatorResponse,
    ValidatorSuccessResponse,
)
from enthusiast_common.agentic_execution.memory import ToolScratchpad

from enthusiast_agent_invoice_scanning.tools.update_stock_levels_tool import (
    StockUpdateMemoryEntry,
    UpdateStockLevelsTool,
)


class AllStockUpdatesSucceededValidator(BaseExecutionValidator):
    """Validates that the stock update tool was called and all SKU updates succeeded.

    If the tool was never called, the agent is asked to retry — it may have returned
    a response without ever invoking the tool. If the tool was called but some SKUs
    failed, the execution is stopped immediately without retry, since individual SKU
    failures in the eCommerce platform cannot be resolved by repeating the same data.
    """

    _TOOL_NAME = UpdateStockLevelsTool.NAME

    def validate(
        self,
        response: str,
        _execution_input: ExecutionInputType,
        tool_scratchpad: ToolScratchpad,
    ) -> ValidatorResponse:
        entry: StockUpdateMemoryEntry | None = tool_scratchpad.read(self._TOOL_NAME)
        if entry is None:
            return ValidatorFailureResponse(
                feedback=(
                    "You returned a response but did not call the stock update tool. "
                    "Read the invoice, extract all SKU/quantity line items, and call "
                    "the stock update tool before responding."
                ),
                retry_needed=True,
            )

        failed_skus = [sku for sku, success in entry.items() if not success]
        if not failed_skus:
            return ValidatorSuccessResponse()

        return ValidatorFailureResponse(
            feedback=(
                f"Stock update failed for the following SKUs: {', '.join(failed_skus)}. "
                "These items could not be updated in the eCommerce platform."
            ),
            retry_needed=False,
        )
