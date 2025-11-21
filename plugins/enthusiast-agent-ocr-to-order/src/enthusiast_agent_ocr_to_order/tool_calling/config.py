from enthusiast_common.config import (
    AgentConfigWithDefaults,
)
from enthusiast_common.config.prompts import ChatPromptTemplateConfig, Message, MessageRole

from .agent import OCROrderToolCallingAgent
from .prompt import OCR_TOOL_CALLING_AGENT_PROMPT


def get_config() -> AgentConfigWithDefaults:
    return AgentConfigWithDefaults(
        prompt_template=ChatPromptTemplateConfig(
            messages=[
                Message(
                    role=MessageRole.SYSTEM,
                    content=OCR_TOOL_CALLING_AGENT_PROMPT,
                ),
                Message(role=MessageRole.PLACEHOLDER, content="{chat_history}"),
                Message(role=MessageRole.USER, content="{input}"),
                Message(role=MessageRole.PLACEHOLDER, content="{agent_scratchpad}"),
            ]
        ),
        agent_class=OCROrderToolCallingAgent,
        tools=OCROrderToolCallingAgent.TOOLS,
    )
