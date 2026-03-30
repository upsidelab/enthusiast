from .base_agent_friendly_error import BaseAgentFriendlyError


class ECommerceConnectorError(BaseAgentFriendlyError):
    """Raised when an e-commerce platform connector encounters an error.

    This is the base error for all ECommercePlatformConnector implementations.
    Agent tools should catch this type to handle connector errors generically,
    regardless of which e-commerce platform is in use.

    Attributes:
        status_code: The HTTP status code returned by the platform API, if applicable.
    """

    def __init__(self, message: str, status_code: int | None = None):
        self.status_code = status_code
        super().__init__(message)

    @property
    def agent_friendly_message(self) -> str:
        return str(self)