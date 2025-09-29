from enthusiast_common.config.base import (
    AgentCallbackHandlerConfig,
    AgentConfigWithDefaults,
    CallbackHandlerConfig,
    LLMConfig,
)
from enthusiast_common.config.prompts import ChatPromptTemplateConfig, Message, MessageRole
from langchain_core.callbacks import StdOutCallbackHandler

from .agent import OCRReActAgent
from .callbacks import AgentActionWebsocketCallbackHandler, ReactAgentWebsocketCallbackHandler
from .prompt import OCR_AGENT_PROMPT


def get_config() -> AgentConfigWithDefaults:
    return AgentConfigWithDefaults(
        chat_prompt_template=ChatPromptTemplateConfig(
            messages=[
                Message(role=MessageRole.SYSTEM, content=OCR_AGENT_PROMPT),
                Message(role=MessageRole.PLACEHOLDER, content="{chat_history}"),
                Message(role=MessageRole.USER, content="{input}"),
                Message(role=MessageRole.AI, content="{agent_scratchpad}"),
            ]
        ),
        agent_class=OCRReActAgent,
        tools=OCRReActAgent.TOOLS,
        llm=LLMConfig(
            callbacks=[
                CallbackHandlerConfig(handler_class=ReactAgentWebsocketCallbackHandler),
                CallbackHandlerConfig(handler_class=StdOutCallbackHandler),
            ],
        ),
        agent_callback_handler=AgentCallbackHandlerConfig(handler_class=AgentActionWebsocketCallbackHandler),
    )
