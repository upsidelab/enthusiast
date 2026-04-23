from abc import ABC, abstractmethod

from .response import ValidatorResponse


class BaseExecutionValidator(ABC):
    """Pluggable validator that inspects a single LLM response string.

    Attach validators to an agentic execution definition class via ``VALIDATORS``. After each
    ``execute()`` call the retry loop runs every validator in order. The first
    failing ``ValidatorResponse`` drives what the loop does next:

    - ``validation_successful=True`` on all validators → execution succeeds.
    - ``validation_successful=False, retry_needed=True`` → feedback is sent back
      to the LLM and the attempt is retried (up to ``MAX_RETRIES`` times).
    - ``validation_successful=False, retry_needed=False`` → the loop stops
      immediately without retrying; ``feedback`` is used as the failure summary.
    """

    @abstractmethod
    def validate(self, response: str) -> ValidatorResponse:
        """Inspect the LLM response and return a structured result.

        Args:
            response: Raw string returned by ``execute()``.

        Returns:
            A :class:`ValidatorResponse` describing whether the response is
            acceptable and, if not, what the loop should do next.
        """
