from dataclasses import dataclass, field
from typing import Any

from .errors import ExecutionFailureCode


@dataclass
class ExecutionResult:
    """The outcome of a completed agent execution.

    Returned by ``BaseAgentExecution.run()``. On success, ``output`` holds the
    structured result (parsed from the LLM's JSON response). On failure,
    ``failure_code`` identifies the cause and ``failure_summary`` contains an
    LLM-generated plain-language explanation.
    """

    success: bool
    output: dict[str, Any] = field(default_factory=dict)
    failure_code: ExecutionFailureCode | None = None
    failure_summary: str | None = None
