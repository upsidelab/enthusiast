from enthusiast_common.agentic_execution import ExecutionInputType
from enthusiast_common.agentic_execution.memory import ToolScratchpad
from enthusiast_common.agentic_execution.validators import BaseExecutionValidator
from enthusiast_common.agentic_execution.validators.failure_response import ValidatorFailureResponse
from enthusiast_common.agentic_execution.validators.success_response import ValidatorSuccessResponse

from enthusiast_agent_order_intake.tools.place_order_tool import PlaceOrderTool


class OrderPlacedValidator(BaseExecutionValidator):
    """Verifies that the place_order tool was called and the order was placed successfully."""

    _TOOL_NAME = PlaceOrderTool.NAME

    def validate(self, response: str, _execution_input: ExecutionInputType, tool_scratchpad: ToolScratchpad):
        entry = tool_scratchpad.read(self._TOOL_NAME)

        if entry is None:
            return ValidatorFailureResponse(
                feedback="You returned a response but did not call the place_order tool. Search for the requested products and place the order.",
                retry_needed=True,
            )

        if not entry.get("success"):
            return ValidatorFailureResponse(
                feedback="The order could not be placed due to a platform error. This cannot be resolved by retrying.",
                retry_needed=False,
            )

        return ValidatorSuccessResponse()
