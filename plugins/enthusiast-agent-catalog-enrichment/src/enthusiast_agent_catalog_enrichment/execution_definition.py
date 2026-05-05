from enthusiast_common.agentic_execution import (
    BaseAgenticExecutionDefinition,
    ExecutionConversationInterface,
    IsValidJsonValidator,
    StopExecutionValidator,
)

from .execution_input import CatalogEnrichmentAgenticExecutionInput
from .validators import AllSkusUpsertedValidator, AllUpsertsSucceededValidator


class CatalogEnrichmentAgenticExecutionDefinition(BaseAgenticExecutionDefinition):
    EXECUTION_KEY = "catalog-enrichment"
    AGENT_KEY = "enthusiast-agent-catalog-enrichment"
    NAME = "Catalog Enrichment"
    INPUT_TYPE = CatalogEnrichmentAgenticExecutionInput
    VALIDATORS = [StopExecutionValidator, IsValidJsonValidator, AllUpsertsSucceededValidator, AllSkusUpsertedValidator]

    def execute(
        self,
        input_data: CatalogEnrichmentAgenticExecutionInput,
        conversation: ExecutionConversationInterface,
    ) -> str:
        return conversation.ask(input_data.additional_instructions or 'Upsert products from given files.')
