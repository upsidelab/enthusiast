from typing import Optional

from .response import ValidatorResponse


class ValidatorFailureResponse(ValidatorResponse):
    """Convenience response for a failing validator.

    Equivalent to ``ValidatorResponse(validation_successful=False, retry_needed=..., feedback=..., failure_code=...)``.

    Args:
        feedback: Plain-language message sent back to the LLM when ``retry_needed``
            is ``True``, or used as ``failure_summary`` when ``retry_needed`` is ``False``.
        retry_needed: Whether the run loop should retry. Defaults to ``True``.
        failure_code: Optional failure code attached to the execution when
            ``retry_needed`` is ``False``. Falls back to ``VALIDATION_FAILED`` if
            not provided. Ignored when ``retry_needed`` is ``True``.
    """

    def __init__(self, feedback: Optional[str] = None, retry_needed: bool = True, failure_code: Optional[str] = None) -> None:
        super().__init__(validation_successful=False, retry_needed=retry_needed, feedback=feedback, failure_code=failure_code)
