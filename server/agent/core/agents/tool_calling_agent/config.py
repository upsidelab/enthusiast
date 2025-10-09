from enthusiast_common.config import AgentConfigWithDefaults
from enthusiast_common.config.prompts import ChatPromptTemplateConfig, Message, MessageRole

from agent.core.agents import ToolCallingAgent


def get_config() -> AgentConfigWithDefaults:
    return AgentConfigWithDefaults(
        prompt_template=ChatPromptTemplateConfig(
            messages=[
                Message(
                    role=MessageRole.SYSTEM,
                    content="You are a sales support agent, and you know everything about a company and their products.",
                ),
                Message(role=MessageRole.PLACEHOLDER, content="{chat_history}"),
                Message(role=MessageRole.USER, content="{input}"),
                Message(role=MessageRole.PLACEHOLDER, content="{agent_scratchpad}"),
            ]
        ),
        agent_class=ToolCallingAgent,
        tools=ToolCallingAgent.TOOLS,
    )
