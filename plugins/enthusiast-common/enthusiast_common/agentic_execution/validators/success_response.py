from .response import ValidatorResponse


class ValidatorSuccessResponse(ValidatorResponse):
    """Convenience response for a passing validator — no arguments required.

    Equivalent to ``ValidatorResponse(validation_successful=True, retry_needed=False, feedback=None)``.
    """

    def __init__(self) -> None:
        super().__init__(validation_successful=True, retry_needed=False, feedback=None)
