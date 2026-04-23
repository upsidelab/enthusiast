from enthusiast_common.agents import BaseAgentConfigProvider, ConfigType
from enthusiast_common.config import AgentConfigWithDefaults, LLMToolConfig

from .agent import CatalogEnrichmentAgent
from .prompt import CATALOG_ENRICHMENT_EXECUTION_SYSTEM_PROMPT, CATALOG_ENRICHMENT_TOOL_CALLING_AGENT_PROMPT
from .tools import StopExecutionTool


class CatalogEnrichmentConfigProvider(BaseAgentConfigProvider):
    def get_config(self, config_type: ConfigType = ConfigType.CONVERSATION) -> AgentConfigWithDefaults:
        if config_type == ConfigType.CONVERSATION:
            system_prompt = CATALOG_ENRICHMENT_TOOL_CALLING_AGENT_PROMPT
            tools = CatalogEnrichmentAgent.TOOLS
        else:
            system_prompt = CATALOG_ENRICHMENT_EXECUTION_SYSTEM_PROMPT
            tools = CatalogEnrichmentAgent.TOOLS + [LLMToolConfig(tool_class=StopExecutionTool)]

        return AgentConfigWithDefaults(
            system_prompt=system_prompt,
            agent_class=CatalogEnrichmentAgent,
            tools=tools,
        )
