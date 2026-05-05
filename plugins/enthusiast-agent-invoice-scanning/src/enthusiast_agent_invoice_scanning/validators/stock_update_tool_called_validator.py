from enthusiast_common.agentic_execution import (
    BaseExecutionValidator,
    ExecutionInputType,
    ValidatorFailureResponse,
    ValidatorResponse,
    ValidatorSuccessResponse,
)
from enthusiast_common.agentic_execution.memory import ToolScratchpad

from enthusiast_agent_invoice_scanning.tools.update_stock_levels_tool import UpdateStockLevelsTool


class StockUpdateToolCalledValidator(BaseExecutionValidator):
    """Ensures the stock update tool was actually called during the execution attempt.

    Guards against the agent producing a valid JSON response without ever invoking
    the update_stock_levels tool — in which case no stock was updated despite a
    seemingly successful response.
    """

    def validate(
        self,
        response: str,
        _execution_input: ExecutionInputType,
        tool_scratchpad: ToolScratchpad,
    ) -> ValidatorResponse:
        entry = tool_scratchpad.read(UpdateStockLevelsTool.NAME)
        if entry is None:
            return ValidatorFailureResponse(
                feedback=(
                    "You returned a response but did not call the stock update tool. "
                    "Read the invoice, extract all SKU/quantity line items, and call "
                    "the stock update tool before responding."
                ),
                retry_needed=True,
            )
        return ValidatorSuccessResponse()
