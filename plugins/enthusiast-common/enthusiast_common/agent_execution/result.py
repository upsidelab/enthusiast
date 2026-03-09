from dataclasses import dataclass, field
from typing import Any


@dataclass
class ExecutionResult:
    """The outcome of a completed agent execution."""

    output: dict[str, Any]
    issues: list[str] = field(default_factory=list)
