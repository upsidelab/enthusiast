from typing import Optional

from enthusiast_common.agentic_execution import (
    BaseAgenticExecutionDefinition,
    ExecutionConversationInterface,
    ExecutionInputType,
)

class CatalogEnrichmentAgenticExecutionInput(ExecutionInputType):
    """Input for the catalog enrichment agentic execution."""
    additional_instructions: Optional[str] = None


class CatalogEnrichmentAgenticExecutionDefinition(BaseAgenticExecutionDefinition):
    EXECUTION_KEY = "catalog-enrichment"
    AGENT_KEY = "enthusiast-agent-catalog-enrichment"
    NAME = "Catalog Enrichment"
    INPUT_TYPE = CatalogEnrichmentAgenticExecutionInput

    def execute(
        self,
        input_data: CatalogEnrichmentAgenticExecutionInput,
        conversation: ExecutionConversationInterface,
    ) -> str:
        return conversation.ask(input_data.additional_instructions or 'Upsert products from given files.')
