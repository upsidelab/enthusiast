from dataclasses import dataclass, field
from typing import Any

from .errors import ExecutionFailureCode


@dataclass
class ExecutionResult:
    """The outcome of a completed agent execution."""

    success: bool
    output: dict[str, Any] = field(default_factory=dict)
    failure_code: ExecutionFailureCode | None = None
    failure_summary: str | None = None
