import json

from ..input import ExecutionInputType
from ..memory import ToolScratchpad
from .base import BaseExecutionValidator
from .failure_response import ValidatorFailureResponse
from .response import ValidatorResponse
from .success_response import ValidatorSuccessResponse


class IsValidJsonValidator(BaseExecutionValidator):
    """Validates that the LLM response is parseable as JSON."""

    FEEDBACK_MESSAGE = (
        "The response is not valid JSON. "
        "Please return the same data as a valid JSON object."
    )

    def validate(self,
                 response: str,
                 _execution_input: ExecutionInputType,
                 _tool_scratchpad: ToolScratchpad) -> ValidatorResponse:
        try:
            json.loads(response)
            return ValidatorSuccessResponse()
        except (json.JSONDecodeError, TypeError):
            return ValidatorFailureResponse(feedback=self.FEEDBACK_MESSAGE)
