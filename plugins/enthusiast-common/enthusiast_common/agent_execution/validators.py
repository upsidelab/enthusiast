import json
from abc import ABC, abstractmethod


class BaseExecutionValidator(ABC):
    """Pluggable validator that inspects a single LLM response string."""

    @abstractmethod
    def validate(self, response: str) -> str | None:
        pass


class IsValidJsonValidator(BaseExecutionValidator):
    """Validates that the LLM response is parseable as JSON."""

    FEEDBACK_MESSAGE = (
        "The response is not valid JSON. "
        "Please return the same data as a valid JSON object."
    )

    def validate(self, response: str) -> str | None:
        try:
            json.loads(response)
            return None
        except (json.JSONDecodeError, TypeError):
            return self.FEEDBACK_MESSAGE
