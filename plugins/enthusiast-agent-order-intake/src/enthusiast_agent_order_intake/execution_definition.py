from enthusiast_common.agentic_execution import (
    BaseAgenticExecutionDefinition,
    ExecutionConversationInterface,
    IsValidJsonValidator,
    StopExecutionValidator,
)

from .execution_input import OrderIntakeAgenticExecutionInput
from .validators import AllQuantitiesCorrectValidator, AllSkusOrderedValidator, OrderPlacedValidator


class OrderIntakeAgenticExecutionDefinition(BaseAgenticExecutionDefinition):
    """Agentic execution definition for the order intake agent.

    Searches for products by SKU and places a single order for all requested items.
    """

    EXECUTION_KEY = "order-intake"
    AGENT_KEY = "enthusiast-agent-order-intake"
    NAME = "Order Intake"
    INPUT_TYPE = OrderIntakeAgenticExecutionInput
    VALIDATORS = [
        StopExecutionValidator,
        IsValidJsonValidator,
        OrderPlacedValidator,
        AllSkusOrderedValidator,
        AllQuantitiesCorrectValidator,
    ]

    def execute(
        self,
        input_data: OrderIntakeAgenticExecutionInput,
        conversation: ExecutionConversationInterface,
    ) -> str:
        items_list = "\n".join(f"- SKU: {item.sku}, quantity: {item.quantity}" for item in input_data.items)
        message = f"Place an order for the following items:\n{items_list}"
        if input_data.additional_instructions:
            message += f"\n\n{input_data.additional_instructions}"
        return conversation.ask(message)
