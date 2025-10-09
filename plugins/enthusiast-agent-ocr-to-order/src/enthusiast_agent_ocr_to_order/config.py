from enthusiast_common.config import (
    AgentCallbackHandlerConfig,
    AgentConfigWithDefaults,
    CallbackHandlerConfig,
    LLMConfig,
)
from enthusiast_common.config.prompts import PromptTemplateConfig
from langchain_core.callbacks import StdOutCallbackHandler

from .agent import OCRReActAgent
from .callbacks import AgentActionWebsocketCallbackHandler, ReactAgentWebsocketCallbackHandler
from .prompt import OCR_AGENT_PROMPT


def get_config() -> AgentConfigWithDefaults:
    return AgentConfigWithDefaults(
        prompt_template=PromptTemplateConfig(
            input_variables=["tools", "tool_names", "input", "agent_scratchpad"], prompt_template=OCR_AGENT_PROMPT
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
