from enthusiast_common.agents import BaseAgentConfigProvider, ConfigType
from enthusiast_common.config import AgentConfigWithDefaults

from .agent import UserManualSearchAgent
from .prompt import USER_MANUAL_TOOL_CALLING_AGENT_PROMPT


class UserManualSearchConfigProvider(BaseAgentConfigProvider):
    def get_config(self, config_type: ConfigType = ConfigType.CONVERSATION) -> AgentConfigWithDefaults:
        return AgentConfigWithDefaults(
            system_prompt=USER_MANUAL_TOOL_CALLING_AGENT_PROMPT,
            agent_class=UserManualSearchAgent,
            tools=UserManualSearchAgent.TOOLS,
        )
