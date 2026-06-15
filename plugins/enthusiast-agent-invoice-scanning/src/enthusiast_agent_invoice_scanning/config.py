from enthusiast_common.agents import BaseAgentConfigProvider, ConfigType
from enthusiast_common.config import AgentConfigWithDefaults, LLMToolConfig

from .agent import InvoiceScanningAgent
from .execution_prompt import INVOICE_SCANNING_EXECUTION_SYSTEM_PROMPT
from .prompt import INVOICE_SCANNING_TOOL_CALLING_AGENT_PROMPT
from .tools import StopExecutionTool


class InvoiceScanningConfigProvider(BaseAgentConfigProvider):
    """Config provider for the Invoice Scanning agent."""

    def get_config(self, config_type: ConfigType = ConfigType.CONVERSATION) -> AgentConfigWithDefaults:
        if config_type == ConfigType.CONVERSATION:
            system_prompt = INVOICE_SCANNING_TOOL_CALLING_AGENT_PROMPT
            tools = InvoiceScanningAgent.TOOLS
        else:
            system_prompt = INVOICE_SCANNING_EXECUTION_SYSTEM_PROMPT
            tools = InvoiceScanningAgent.TOOLS + [LLMToolConfig(tool_class=StopExecutionTool)]

        return AgentConfigWithDefaults(
            system_prompt=system_prompt,
            agent_class=InvoiceScanningAgent,
            tools=tools,
        )
