from typing import Optional

from .response import ValidatorResponse


class ValidatorFailureResponse(ValidatorResponse):
    """Convenience response for a failing validator.

    Equivalent to ``ValidatorResponse(validation_successful=False, retry_needed=..., feedback=...)``.

    Args:
        feedback: Plain-language message sent back to the LLM when ``retry_needed``
            is ``True``, or used as ``failure_summary`` when ``retry_needed`` is ``False``.
        retry_needed: Whether the run loop should retry. Defaults to ``True``.
    """

    def __init__(self, feedback: Optional[str] = None, retry_needed: bool = True) -> None:
        super().__init__(validation_successful=False, retry_needed=retry_needed, feedback=feedback)
