from enthusiast_common.errors import RetrieverError


class RetrieverSQLPermissionError(RetrieverError):
    def __init__(self, message: str):
        self._message = message

    @property
    def agent_friendly_message(self) -> str:
        return f"The provided SQL query cannot be executed {self._message}. Fix it and try again."
