from enthusiast_common.errors import RetrieverError


class RetrieverSQLExecutionError(RetrieverError):
    @property
    def agent_friendly_message(self) -> str:
        return f"The SQL query failed with the following error {self.__cause__}. Fix it and try again."
