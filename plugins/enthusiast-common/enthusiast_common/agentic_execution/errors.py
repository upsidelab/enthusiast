class ExecutionFailureCode:
    """Standardised failure codes stored on ``AgenticExecution.failure_code``.

    Each constant is a plain string, so they can be compared directly against
    the database value. The class is intentionally not an enum so that plugins
    can subclass it to add domain-specific codes and point
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
    VALIDATION_FAILED = "validation_failed"
    """A validator rejected the response and explicitly indicated that retrying is not useful."""
    UNKNOWN = "unknown"
    """The execution reported failure but did not provide a failure code."""
