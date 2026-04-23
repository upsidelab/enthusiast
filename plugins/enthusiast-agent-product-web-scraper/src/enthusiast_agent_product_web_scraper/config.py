from enthusiast_common.agents import BaseAgentConfigProvider, ConfigType
from enthusiast_common.config import AgentConfigWithDefaults

from .agent import ProductWebScraperAgent
from .execution_prompt import PRODUCT_WEB_SCRAPER_EXECUTION_PROMPT
from .prompt import PRODUCT_WEB_SCRAPER_CONVERSATION_PROMPT


class ProductWebScraperConfigProvider(BaseAgentConfigProvider):
    """Config provider for the Product Web Scraper agent.

    Returns agent configuration appropriate for the requested context type.
    """


    def get_config(self, config_type: ConfigType = ConfigType.CONVERSATION) -> AgentConfigWithDefaults:
        system_prompt = (
            PRODUCT_WEB_SCRAPER_CONVERSATION_PROMPT
            if config_type == ConfigType.CONVERSATION
            else PRODUCT_WEB_SCRAPER_EXECUTION_PROMPT
        )
        return AgentConfigWithDefaults(
            system_prompt=system_prompt,
            agent_class=ProductWebScraperAgent,
            tools=ProductWebScraperAgent.TOOLS,
        )
