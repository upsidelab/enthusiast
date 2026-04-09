import json
from abc import ABC, abstractmethod
from typing import Optional


class BaseExecutionValidator(ABC):
    """Pluggable validator that inspects a single LLM response string.

    Attach validators to an agentic execution definition class via ``VALIDATORS``. After each
    ``execute()`` call the retry loop runs every validator in order. The first
    non-``None`` return value is sent back to the LLM as a correction prompt and
    the attempt is retried. If all validators return ``None`` the response is
    considered valid and the execution finishes successfully.
    """

    @abstractmethod
    def validate(self, response: str) -> Optional[str]:
        """Inspect the LLM response and return feedback or ``None``.

        Args:
            response: Raw string returned by ``execute()``.

        Returns:
            ``None`` if the response is acceptable, or a plain-language feedback
            string to send back to the LLM for correction.
        """


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
