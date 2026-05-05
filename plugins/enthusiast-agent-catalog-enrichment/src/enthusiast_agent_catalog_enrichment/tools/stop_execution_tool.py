from enthusiast_common.agentic_execution import StopExecutionValidator
from enthusiast_common.tools.base import BaseLLMTool
from pydantic import BaseModel, Field


class StopExecutionInput(BaseModel):
    stop_reason: str = Field(
        description="A clear, concise explanation of why the execution cannot continue."
    )


class StopExecutionTool(BaseLLMTool):
    """Tool the agent calls to permanently halt the execution run.

    Use this ONLY when further progress is impossible — for example when required
    product data is absent from all available sources, or when a critical system
    dependency (such as an eCommerce connector) is not configured.

    Do NOT call this for retryable failures such as partial upsert errors that might
    succeed with corrected data. Provide a concise ``stop_reason`` that explains why
    the execution must stop; it will be surfaced as the execution failure summary.
    """

    NAME = StopExecutionValidator.TOOL_NAME
    DESCRIPTION = (
        "Signal that the execution cannot continue and should stop immediately. "
        "Call this ONLY when further progress is impossible — for example when required "
        "data is absent from all available sources, or a critical system dependency "
        "(such as an eCommerce connector) is not configured. "
        "Do NOT call this for retryable failures. "
        "Provide a concise reason explaining why the execution must stop."
    )
    ARGS_SCHEMA = StopExecutionInput
    RETURN_DIRECT = False

    def run(self, stop_reason: str) -> str:
        if self._injector:
            self._injector.tool_scratchpad.record(self.NAME, stop_reason)
        return "Execution stop registered."
