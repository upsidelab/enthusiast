from pydantic import BaseModel


class ExecutionInputType(BaseModel):
    """Base class for agentic execution input payloads.

    Subclass this in each agent plugin to declare the structured input that a
    specific agentic execution definition class accepts. Fields are validated by the server before
    the execution record is created, and the JSON schema is derived from this
    class and returned by the ``GET /api/agents/<id>/agentic-execution-definitions/`` endpoint.

    Extra fields are forbidden — any unknown key in the request body is rejected
    with a 400 error.

    Example::

        class CatalogEnrichmentAgenticExecutionInput(ExecutionInputType):
            additional_instructions: Optional[str] = None
    """

    model_config = {"extra": "forbid"}
