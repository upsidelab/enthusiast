from typing import Optional

from enthusiast_common.agentic_execution.input import ExecutionInputType
from enthusiast_common.agentic_execution.memory import ToolResultMemory
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
        tool_result_memory: Optional[ToolResultMemory] = None,
    ) -> ValidatorResponse:
        if tool_result_memory is None:
            return ValidatorSuccessResponse()

        results = tool_result_memory.get_results(self.TOOL_NAME)
        if not results:
            return ValidatorSuccessResponse()

        return ValidatorFailureResponse(feedback=results[0].result, retry_needed=False)
