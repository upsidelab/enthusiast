from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ValidatorResponse:
    """Structured response returned by a validator.

    Attributes:
        validation_successful: Whether the response passed validation.
        retry_needed: Whether the run loop should retry after a failure. Set to
            ``False`` when retrying is pointless — e.g. when an external system
            is unreachable and the LLM cannot fix that by producing a different
            response. Ignored when ``validation_successful`` is ``True``.
        feedback: Plain-language message to send back to the LLM when
            ``validation_successful`` is ``False`` and ``retry_needed`` is ``True``.
            Also used as the ``failure_summary`` when ``retry_needed`` is ``False``.
    """

    validation_successful: bool
    retry_needed: bool
    feedback: Optional[str] = field(default=None)
