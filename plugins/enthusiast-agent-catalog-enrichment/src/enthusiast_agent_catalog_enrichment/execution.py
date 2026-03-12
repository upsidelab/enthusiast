from typing import Optional

from enthusiast_common.agent_execution import (
    BaseAgentExecution,
    ExecutionConversationInterface,
    ExecutionInputType,
)

class CatalogEnrichmentExecutionInput(ExecutionInputType):
    """Input for the catalog enrichment batch execution."""
    additional_instructions: Optional[str] = None


class CatalogEnrichmentExecution(BaseAgentExecution):
    EXECUTION_KEY = "catalog-enrichment"
    AGENT_KEY = "enthusiast-agent-catalog-enrichment"
    NAME = "Catalog Enrichment"
    INPUT_TYPE = CatalogEnrichmentExecutionInput

    def execute(
        self,
        input_data: CatalogEnrichmentExecutionInput,
        conversation: ExecutionConversationInterface,
    ) -> str:
        return conversation.ask(input_data.additional_instructions or 'Upsert products from given files.')
