from enum import Enum


class ExecutionStatus(str, Enum):
    """Lifecycle status of an agentic execution."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    FINISHED = "finished"
    FAILED = "failed"
