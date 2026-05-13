from enthusiast_common.agentic_execution import (
    BaseAgenticExecutionDefinition,
    ExecutionConversationInterface,
    IsValidJsonValidator,
    StopExecutionValidator,
)

from .execution_input import OrderIntakeAgenticExecutionInput
from .validators import OrderPlacedValidator


class OrderIntakeAgenticExecutionDefinition(BaseAgenticExecutionDefinition):
    """Agentic execution definition for the order intake agent.

    Reads an attached purchase order document, extracts line items, and places
    a single order for all items in the configured eCommerce platform.
    """

    EXECUTION_KEY = "order-intake"
    AGENT_KEY = "enthusiast-agent-order-intake"
    NAME = "Order Intake"
    INPUT_TYPE = OrderIntakeAgenticExecutionInput
    VALIDATORS = [
        StopExecutionValidator,
        IsValidJsonValidator,
        OrderPlacedValidator,
    ]

    def execute(
        self,
        input_data: OrderIntakeAgenticExecutionInput,
        conversation: ExecutionConversationInterface,
    ) -> str:
        return conversation.ask(
            input_data.additional_instructions or "Process the attached purchase order and create an order."
        )
