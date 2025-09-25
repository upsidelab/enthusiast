from enthusiast_common.config.base import AgentConfigWithDefaults
from enthusiast_common.config.prompts import ChatPromptTemplateConfig

from agent.core.agents import ToolCallingAgent


def get_config() -> AgentConfigWithDefaults:
    return AgentConfigWithDefaults(
        chat_prompt_template=ChatPromptTemplateConfig(
            messages=[
                (
                    "system",
                    "You are a sales support agent, and you know everything about a company and their products.",
                ),
                ("placeholder", "{chat_history}"),
                ("human", "{input}"),
                ("placeholder", "{agent_scratchpad}"),
            ]
        ),
        agent_class=ToolCallingAgent,
        tools=ToolCallingAgent.TOOLS,
    )
