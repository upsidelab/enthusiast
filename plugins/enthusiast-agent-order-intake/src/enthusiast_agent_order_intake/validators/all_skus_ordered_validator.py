import json

from enthusiast_common.agentic_execution import (
    BaseExecutionValidator,
    ValidatorFailureResponse,
    ValidatorResponse,
    ValidatorSuccessResponse,
)
from enthusiast_common.agentic_execution.memory import ToolScratchpad

from enthusiast_agent_order_intake.execution_input import OrderIntakeAgenticExecutionInput


class AllSkusOrderedValidator(BaseExecutionValidator):
    """Verifies that all SKUs from the input were included in the placed order."""

    def validate(self, response: str, execution_input: OrderIntakeAgenticExecutionInput, tool_scratchpad: ToolScratchpad) -> ValidatorResponse:
        data = json.loads(response)
        ordered_items: dict = data.get("ordered_items", {})

        expected_skus = [item.sku for item in execution_input.items]
        missing_skus = [sku for sku in expected_skus if sku not in ordered_items]

        if not missing_skus:
            return ValidatorSuccessResponse()

        skus_list = ", ".join(missing_skus)
        return ValidatorFailureResponse(
            feedback=f"The following SKUs were not included in the order: {skus_list}. Search for these products and place the order again with all requested items.",
            retry_needed=True,
        )
