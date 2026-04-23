from enthusiast_common.agents import BaseAgentConfigProvider, ConfigType
from enthusiast_common.config import AgentConfigWithDefaults

from .agent import InvoiceScanningAgent
from .prompt import INVOICE_SCANNING_AGENT_PROMPT


class InvoiceScanningConfigProvider(BaseAgentConfigProvider):
    """Config provider for the Invoice Scanning agent."""

    def get_config(self, config_type: ConfigType = ConfigType.CONVERSATION) -> AgentConfigWithDefaults:
        return AgentConfigWithDefaults(
            system_prompt=INVOICE_SCANNING_AGENT_PROMPT,
            agent_class=InvoiceScanningAgent,
            tools=InvoiceScanningAgent.TOOLS,
        )
