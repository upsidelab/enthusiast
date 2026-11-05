from suvereo_agent_tools import StopExecutionTool
from suvereo_common.agentic_execution import (
    BaseAgenticExecutionDefinition,
    ExecutionConversationInterface,
    IsValidJsonValidator,
    StopExecutionValidator,
)
from suvereo_common.config import LLMToolConfig

from .agent import CatalogEnrichmentAgent
from .execution_input import CatalogEnrichmentAgenticExecutionInput
from .prompt import CATALOG_ENRICHMENT_EXECUTION_SYSTEM_PROMPT
from .validators import AllSkusUpsertedValidator, AllUpsertsSucceededValidator


class CatalogEnrichmentAgenticExecutionDefinition(BaseAgenticExecutionDefinition):
    EXECUTION_KEY = "catalog-enrichment"
    AGENT_KEY = "enthusiast-agent-catalog-enrichment"
    NAME = "Catalog Enrichment"
    INPUT_TYPE = CatalogEnrichmentAgenticExecutionInput
    VALIDATORS = [StopExecutionValidator, IsValidJsonValidator, AllUpsertsSucceededValidator, AllSkusUpsertedValidator]
    SYSTEM_PROMPT = CATALOG_ENRICHMENT_EXECUTION_SYSTEM_PROMPT
    TOOLS = [*CatalogEnrichmentAgent.TOOLS, LLMToolConfig(tool_class=StopExecutionTool)]

    def execute(
        self,
        input_data: CatalogEnrichmentAgenticExecutionInput,
        conversation: ExecutionConversationInterface,
    ) -> str:
        return conversation.ask(input_data.additional_instructions or 'Upsert products from given files.')
