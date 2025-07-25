from enthusiast_common.config import AgentConfigWithDefaults, LLMToolConfig
from enthusiast_common.config.base import ChatPromptTemplateConfig

from agent.core.agents import ToolCallingAgent
from agent.tools import CreateAnswerTool


def get_config(conversation_id: int, streaming: bool) -> AgentConfigWithDefaults:
    return AgentConfigWithDefaults(
        conversation_id=conversation_id,
        prompt_template=ChatPromptTemplateConfig(
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
        llm_tools=[
            LLMToolConfig(
                tool_class=CreateAnswerTool,
            )
        ],
    )
