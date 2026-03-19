from enthusiast_common.agents import BaseAgentConfigProvider, ConfigType
from enthusiast_common.config import (
    AgentConfigWithDefaults,
)
from enthusiast_common.config.prompts import ChatPromptTemplateConfig, Message, MessageRole

from .agent import OrderIntakeAgent
from .prompt import ORDER_INTAKE_TOOL_CALLING_AGENT_PROMPT

class OrderIntakeConfigProvider(BaseAgentConfigProvider):
    def get_config(self, config_type: ConfigType = ConfigType.CONVERSATION) -> AgentConfigWithDefaults:
        return AgentConfigWithDefaults(
            prompt_template=ChatPromptTemplateConfig(
                messages=[
                    Message(
                        role=MessageRole.SYSTEM,
                        content=ORDER_INTAKE_TOOL_CALLING_AGENT_PROMPT,
                    ),
                    Message(role=MessageRole.PLACEHOLDER, content="{chat_history}"),
                    Message(role=MessageRole.USER, content="{input}"),
                    Message(role=MessageRole.PLACEHOLDER, content="{agent_scratchpad}"),
                ]
            ),
            agent_class=OrderIntakeAgent,
            tools=OrderIntakeAgent.TOOLS,
        )
