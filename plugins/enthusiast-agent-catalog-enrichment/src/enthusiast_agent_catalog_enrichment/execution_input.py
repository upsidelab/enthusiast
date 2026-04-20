from typing import Optional

from enthusiast_common.agentic_execution import ExecutionInputType


class CatalogEnrichmentAgenticExecutionInput(ExecutionInputType):
    """Input for the catalog enrichment agentic execution."""
    additional_instructions: Optional[str] = None
    skus: Optional[list[str]] = None
