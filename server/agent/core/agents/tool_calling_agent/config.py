from enthusiast_common.config import AgentConfig, AgentConfigWithDefaults, LLMConfig, LLMToolConfig
from langchain_core.prompts import ChatPromptTemplate

from agent.callbacks import ConversationWebSocketCallbackHandler
from agent.core.agents import ToolCallingAgent
from agent.core.agents.default_config import merge_config
from agent.models import Conversation
from agent.tools import CreateAnswerTool


def get_config(conversation: Conversation, streaming: bool) -> AgentConfig:
    base_config = AgentConfigWithDefaults(
        conversation_id=conversation.id,
        prompt_template=ChatPromptTemplate.from_messages(
            [
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
        llm=LLMConfig(callbacks=[ConversationWebSocketCallbackHandler(conversation.id)], streaming=streaming),
    )
    return merge_config(base_config)
