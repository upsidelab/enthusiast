from enthusiast_common.agentic_execution import (
    BaseAgenticExecutionDefinition,
    ExecutionConversationInterface,
    IsValidJsonValidator,
    StopExecutionValidator,
)

from .execution_input import InvoiceScanningAgenticExecutionInput
from .validators import AllSkusUpdatedValidator, AllStockUpdatesSucceededValidator


class InvoiceScanningAgenticExecutionDefinition(BaseAgenticExecutionDefinition):
    """Agentic execution definition for the invoice scanning agent.

    Reads the attached invoice, extracts SKU/quantity line items, and updates stock
    levels in the configured eCommerce platform.
    """

    EXECUTION_KEY = "invoice-scanning"
    AGENT_KEY = "enthusiast-agent-invoice-scanning"
    NAME = "Invoice Scanning"
    INPUT_TYPE = InvoiceScanningAgenticExecutionInput
    VALIDATORS = [
        StopExecutionValidator,
        IsValidJsonValidator,
        AllStockUpdatesSucceededValidator,
        AllSkusUpdatedValidator,
    ]

    def execute(
        self,
        input_data: InvoiceScanningAgenticExecutionInput,
        conversation: ExecutionConversationInterface,
    ) -> str:
        return conversation.ask(
            input_data.additional_instructions or "Process the attached invoice and update stock levels."
        )
