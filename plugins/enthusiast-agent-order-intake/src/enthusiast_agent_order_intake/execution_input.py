from enthusiast_common.agentic_execution import ExecutionInputType


class OrderIntakeAgenticExecutionInput(ExecutionInputType):
    """Input for the order intake agentic execution."""

    additional_instructions: str | None = None
