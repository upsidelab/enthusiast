from enthusiast_common.config import (
    AgentConfigWithDefaults,
)
from enthusiast_common.config.prompts import PromptTemplateConfig

from .agent import OCROrderReActAgent
from .prompt import OCR_AGENT_PROMPT


def get_config() -> AgentConfigWithDefaults:
    return AgentConfigWithDefaults(
        prompt_template=PromptTemplateConfig(
            input_variables=["tools", "tool_names", "input", "agent_scratchpad"], prompt_template=OCR_AGENT_PROMPT
        ),
        agent_class=OCROrderReActAgent,
        tools=OCROrderReActAgent.TOOLS,
    )
