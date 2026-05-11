from enthusiast_common.agents import BaseAgentConfigProvider, ConfigType
from enthusiast_common.config import AgentConfigWithDefaults

from .agent import OrderIntakeAgent
from .execution_prompt import ORDER_INTAKE_EXECUTION_SYSTEM_PROMPT
from .prompt import ORDER_INTAKE_TOOL_CALLING_AGENT_PROMPT


class OrderIntakeConfigProvider(BaseAgentConfigProvider):
    def get_config(self, config_type: ConfigType = ConfigType.CONVERSATION) -> AgentConfigWithDefaults:
        system_prompt = (
            ORDER_INTAKE_TOOL_CALLING_AGENT_PROMPT
            if config_type == ConfigType.CONVERSATION
            else ORDER_INTAKE_EXECUTION_SYSTEM_PROMPT
        )
        return AgentConfigWithDefaults(
            system_prompt=system_prompt,
            agent_class=OrderIntakeAgent,
            tools=OrderIntakeAgent.TOOLS,
        )
