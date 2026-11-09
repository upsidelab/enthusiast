from typing import Optional


class ECommerceConnectorError(Exception):
    """Raised when communication with an e-commerce platform fails."""

    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.status_code = status_code
