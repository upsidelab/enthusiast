from enthusiast_common.agentic_execution import ExecutionInputType


class CatalogWebImportExecutionInput(ExecutionInputType):
    """Input for the catalog web import agentic execution."""

    urls: list[str]
    additional_instructions: str | None = None
