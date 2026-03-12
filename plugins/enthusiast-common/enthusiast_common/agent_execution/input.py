from pydantic import BaseModel


class ExecutionInputType(BaseModel):
    """Base class for execution input payloads.

    Subclass this in each agent plugin to declare the structured input that a
    specific execution class accepts. Fields are validated by the server before
    the execution record is created, and the JSON schema is derived from this
    class and returned by the ``GET /api/agents/<id>/execution-types/`` endpoint.

    Extra fields are forbidden — any unknown key in the request body is rejected
    with a 400 error.

    Example::

        class CatalogEnrichmentExecutionInput(ExecutionInputType):
            additional_instructions: Optional[str] = None
    """

    model_config = {"extra": "forbid"}