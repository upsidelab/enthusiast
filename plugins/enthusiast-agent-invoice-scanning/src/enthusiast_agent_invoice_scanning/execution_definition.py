from suvereo_common.agentic_execution import (
    BaseAgenticExecutionDefinition,
    ExecutionConversationInterface,
    IsValidJsonValidator,
    StopExecutionValidator,
)
from suvereo_common.config import LLMToolConfig

from .agent import InvoiceScanningAgent
from .execution_input import InvoiceScanningAgenticExecutionInput
from .execution_prompt import INVOICE_SCANNING_EXECUTION_SYSTEM_PROMPT
from .tools import StopExecutionTool
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
    SYSTEM_PROMPT = INVOICE_SCANNING_EXECUTION_SYSTEM_PROMPT
    TOOLS = [*InvoiceScanningAgent.TOOLS, LLMToolConfig(tool_class=StopExecutionTool)]

    def execute(
        self,
        input_data: InvoiceScanningAgenticExecutionInput,
        conversation: ExecutionConversationInterface,
    ) -> str:
        return conversation.ask(
            input_data.additional_instructions or "Process the attached invoice and update stock levels."
        )
