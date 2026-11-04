from typing import Optional

from suvereo_common.agentic_execution import ExecutionInputType


class InvoiceScanningAgenticExecutionInput(ExecutionInputType):
    """Input for the invoice scanning agentic execution."""

    additional_instructions: Optional[str] = None
    skus: Optional[list[str]] = None
