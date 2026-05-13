from dataclasses import dataclass, field
from typing import Any


@dataclass
class ExecutionResult:
    """The outcome of a completed agentic execution.

    Returned by ``BaseAgenticExecutionDefinition.run()``. On success, ``output`` holds the
    structured result (parsed from the LLM's JSON response). On failure,
    ``failure_code`` identifies the cause and ``failure_summary`` contains an
    LLM-generated plain-language explanation.
    """

    success: bool
    output: dict[str, Any] = field(default_factory=dict)
    failure_code: str | None = None
    failure_summary: str | None = None
