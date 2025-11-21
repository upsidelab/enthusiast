from enthusiast_common.config import AgentConfigWithDefaults
from enthusiast_common.config.prompts import PromptTemplateConfig

from .agent import InvoiceScanningReActAgent
from .prompt import INVOICE_SCANNING_RE_ACT_AGENT_PROMPT


def get_config() -> AgentConfigWithDefaults:
    return AgentConfigWithDefaults(
        prompt_template=PromptTemplateConfig(
            input_variables=["tools", "tool_names", "input", "agent_scratchpad", "data_format"],
            prompt_template=INVOICE_SCANNING_RE_ACT_AGENT_PROMPT,
        ),
        agent_class=InvoiceScanningReActAgent,
        tools=InvoiceScanningReActAgent.TOOLS,
    )
