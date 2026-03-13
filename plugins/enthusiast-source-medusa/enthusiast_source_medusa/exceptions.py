class MedusaAPIError(Exception):
    """Raised when the Medusa API returns an error response."""

    def __init__(self, message: str, status_code: int | None = None):
        self.status_code = status_code
        super().__init__(message)
