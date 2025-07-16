from enthusiast_common.config import AgentConfigWithDefaults, LLMConfig, LLMToolConfig
from langchain_core.prompts import ChatPromptTemplate

from agent.callbacks import ConversationWebSocketCallbackHandler
from agent.core.agents import ToolCallingAgent
from agent.tools import CreateAnswerTool


def get_config(conversation_id: int, streaming: bool) -> AgentConfigWithDefaults:
    return AgentConfigWithDefaults(
        conversation_id=conversation_id,
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
        llm=LLMConfig(callbacks=[ConversationWebSocketCallbackHandler(conversation_id)], streaming=streaming),
    )
