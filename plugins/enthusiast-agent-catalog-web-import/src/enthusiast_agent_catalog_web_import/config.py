from enthusiast_agent_catalog_enrichment.tools import StopExecutionTool
from enthusiast_common.agents import BaseAgentConfigProvider, ConfigType
from enthusiast_common.config import AgentConfigWithDefaults, LLMToolConfig

from .agent import CatalogWebImportAgent
from .execution_prompt import CATALOG_WEB_IMPORT_EXECUTION_PROMPT
from .prompt import CATALOG_WEB_IMPORT_CONVERSATION_PROMPT


class CatalogWebImportConfigProvider(BaseAgentConfigProvider):
    """Config provider for the Catalog Web Import agent.

    Returns agent configuration appropriate for the requested context type.
    """

    def get_config(self, config_type: ConfigType = ConfigType.CONVERSATION) -> AgentConfigWithDefaults:
        if config_type == ConfigType.CONVERSATION:
            system_prompt = CATALOG_WEB_IMPORT_CONVERSATION_PROMPT
            tools = CatalogWebImportAgent.TOOLS
        else:
            system_prompt = CATALOG_WEB_IMPORT_EXECUTION_PROMPT
            tools = CatalogWebImportAgent.TOOLS + [LLMToolConfig(tool_class=StopExecutionTool)]

        return AgentConfigWithDefaults(
            system_prompt=system_prompt,
            agent_class=CatalogWebImportAgent,
            tools=tools,
        )
