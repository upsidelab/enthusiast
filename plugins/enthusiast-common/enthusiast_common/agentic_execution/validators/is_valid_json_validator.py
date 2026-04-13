import json
from typing import Optional

from ..memory import ToolResultMemory
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

    def validate(self, response: str, tool_result_memory: Optional[ToolResultMemory] = None) -> ValidatorResponse:
        try:
            json.loads(response)
            return ValidatorSuccessResponse()
        except (json.JSONDecodeError, TypeError):
            return ValidatorFailureResponse(feedback=self.FEEDBACK_MESSAGE)
