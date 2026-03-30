from enthusiast_common.agents import BaseAgentConfigProvider, ConfigType
from enthusiast_common.config import AgentConfigWithDefaults

from .agent import OrderIntakeAgent
from .prompt import ORDER_INTAKE_TOOL_CALLING_AGENT_PROMPT

class OrderIntakeConfigProvider(BaseAgentConfigProvider):
    def get_config(self, config_type: ConfigType = ConfigType.CONVERSATION) -> AgentConfigWithDefaults:
        return AgentConfigWithDefaults(
            system_prompt=ORDER_INTAKE_TOOL_CALLING_AGENT_PROMPT,
            agent_class=OrderIntakeAgent,
            tools=OrderIntakeAgent.TOOLS,
        )
