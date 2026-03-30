from enthusiast_common.agents import BaseAgentConfigProvider, ConfigType
from enthusiast_common.config import AgentConfigWithDefaults

from .agent import CatalogEnrichmentAgent
from .prompt import CATALOG_ENRICHMENT_TOOL_CALLING_AGENT_PROMPT, CATALOG_ENRICHMENT_EXECUTION_SYSTEM_PROMPT


class CatalogEnrichmentConfigProvider(BaseAgentConfigProvider):
    def get_config(self, config_type: ConfigType = ConfigType.CONVERSATION) -> AgentConfigWithDefaults:
        system_prompt = (
            CATALOG_ENRICHMENT_TOOL_CALLING_AGENT_PROMPT
            if config_type == ConfigType.CONVERSATION
            else CATALOG_ENRICHMENT_EXECUTION_SYSTEM_PROMPT
        )
        return AgentConfigWithDefaults(
            system_prompt=system_prompt,
            agent_class=CatalogEnrichmentAgent,
            tools=CatalogEnrichmentAgent.TOOLS,
        )
