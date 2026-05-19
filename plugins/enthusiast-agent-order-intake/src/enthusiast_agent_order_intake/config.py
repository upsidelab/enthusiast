from enthusiast_common.agents import BaseAgentConfigProvider, ConfigType
from enthusiast_common.config import AgentConfigWithDefaults, LLMToolConfig

from .agent import OrderIntakeAgent
from .execution_prompt import ORDER_INTAKE_EXECUTION_SYSTEM_PROMPT
from .prompt import ORDER_INTAKE_TOOL_CALLING_AGENT_PROMPT
from .tools import StopExecutionTool


class OrderIntakeConfigProvider(BaseAgentConfigProvider):
    def get_config(self, config_type: ConfigType = ConfigType.CONVERSATION) -> AgentConfigWithDefaults:
        if config_type == ConfigType.CONVERSATION:
            system_prompt = ORDER_INTAKE_TOOL_CALLING_AGENT_PROMPT
            tools = OrderIntakeAgent.TOOLS
        else:
            system_prompt = ORDER_INTAKE_EXECUTION_SYSTEM_PROMPT
            tools = OrderIntakeAgent.TOOLS + [LLMToolConfig(tool_class=StopExecutionTool)]

        return AgentConfigWithDefaults(
            system_prompt=system_prompt,
            agent_class=OrderIntakeAgent,
            tools=tools,
        )
