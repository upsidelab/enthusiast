from enthusiast_common.agents import BaseAgentConfigProvider, ConfigType
from enthusiast_common.config import AgentConfigWithDefaults

from .agent import ProductSearchAgent
from .prompt import PRODUCT_SEARCH_TOOL_CALLING_AGENT_PROMPT


class ProductSearchConfigProvider(BaseAgentConfigProvider):
    def get_config(self, config_type: ConfigType = ConfigType.CONVERSATION) -> AgentConfigWithDefaults:
        return AgentConfigWithDefaults(
            system_prompt=PRODUCT_SEARCH_TOOL_CALLING_AGENT_PROMPT,
            agent_class=ProductSearchAgent,
            tools=ProductSearchAgent.TOOLS,
        )
