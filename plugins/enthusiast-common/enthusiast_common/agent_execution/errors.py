from enum import StrEnum


class ExecutionFailureCode(StrEnum):
    RUNTIME_ERROR = "runtime_error"
    MAX_RETRIES_EXCEEDED = "max_retries_exceeded"