import json

from enthusiast_common.agentic_execution import (
    BaseExecutionValidator,
    ValidatorFailureResponse,
    ValidatorResponse,
    ValidatorSuccessResponse,
)
from enthusiast_common.agentic_execution.memory import ToolScratchpad

from enthusiast_agent_order_intake.execution_input import OrderIntakeAgenticExecutionInput


class AllQuantitiesCorrectValidator(BaseExecutionValidator):
    """Verifies that ordered quantities match the requested amounts for each SKU."""

    def validate(self, response: str, execution_input: OrderIntakeAgenticExecutionInput, tool_scratchpad: ToolScratchpad) -> ValidatorResponse:
        data = json.loads(response)
        ordered_items: dict = data.get("ordered_items", {})

        mismatched = [
            f"{item.sku} (expected {item.quantity}, got {ordered_items[item.sku]})"
            for item in execution_input.items
            if item.sku in ordered_items and int(ordered_items[item.sku]) != item.quantity
        ]

        if not mismatched:
            return ValidatorSuccessResponse()

        items_str = ", ".join(mismatched)
        return ValidatorFailureResponse(
            feedback=f"The following items have incorrect quantities: {items_str}. Place the order again with the correct quantities.",
            retry_needed=True,
        )
