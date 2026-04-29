from enthusiast_common.agentic_execution.input import ExecutionInputType
from enthusiast_common.agentic_execution.memory import ToolScratchpad

from .base import BaseExecutionValidator
from .failure_response import ValidatorFailureResponse
from .response import ValidatorResponse
from .success_response import ValidatorSuccessResponse


class StopExecutionValidator(BaseExecutionValidator):
    """Stops the run immediately when the agent called the stop_execution tool.

    If the agent determined that further progress is impossible and recorded a stop
    reason via ``stop_execution``, this validator surfaces that reason as a
    non-retryable failure so the run loop terminates without issuing further LLM calls.
    """

    TOOL_NAME = "stop_execution"

    def validate(
        self,
        response: str,
        _execution_input: ExecutionInputType,
        tool_scratchpad: ToolScratchpad,
    ) -> ValidatorResponse:
        result = tool_scratchpad.read(self.TOOL_NAME)
        if result is None:
            return ValidatorSuccessResponse()

        return ValidatorFailureResponse(feedback=result, retry_needed=False)
