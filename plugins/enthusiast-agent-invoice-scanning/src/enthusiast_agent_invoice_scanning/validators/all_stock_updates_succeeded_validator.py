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
    """Fails the execution immediately when any SKU stock update was unsuccessful.

    Reads the ToolScratchpad entry recorded by UpdateStockLevelsTool. If any SKU
    mapped to False (update failed or errored), the execution is stopped without retry
    — individual SKU failures in the eCommerce platform cannot be fixed by the LLM
    retrying the same data.
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
            return ValidatorSuccessResponse()

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
