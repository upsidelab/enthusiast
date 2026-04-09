from enum import StrEnum


class ExecutionFailureCode(StrEnum):
    """Standardised failure codes stored on ``AgenticExecution.failure_code``.

    Plugins may subclass this to add domain-specific codes and point
    ``BaseAgenticExecutionDefinition.FAILURE_CODES`` at the subclass::

        class MyFailureCode(ExecutionFailureCode):
            CUSTOM_REASON = "custom_reason"

        class MyExecution(BaseAgenticExecutionDefinition):
            FAILURE_CODES = MyFailureCode
    """

    RUNTIME_ERROR = "runtime_error"
    """An unexpected exception escaped the execution — set by the Celery task's ``on_failure`` hook."""
    MAX_RETRIES_EXCEEDED = "max_retries_exceeded"
    """The LLM failed to produce a valid response after ``MAX_RETRIES`` correction cycles."""
    UNKNOWN = "unknown"
    """The execution reported failure but did not provide a failure code."""
