from enthusiast_domain.builder import EcommerceAgentBuilder
from enthusiast_domain_tools import ProductExamplesTool, ProductSQLSearchTool
from suvereo_agent_tool_calling import BaseToolCallingAgent
from suvereo_common.config.base import LLMToolConfig

from .prompt import ORDER_INTAKE_TOOL_CALLING_AGENT_PROMPT
from .tools.place_order_tool import PlaceOrderTool


class OrderIntakeAgent(BaseToolCallingAgent):
    AGENT_KEY = "enthusiast-agent-order-intake"
    NAME = "Order Intake"
    SYSTEM_PROMPT = ORDER_INTAKE_TOOL_CALLING_AGENT_PROMPT
    BUILDER_CLASS = EcommerceAgentBuilder
    TOOLS = [
        LLMToolConfig(tool_class=ProductExamplesTool),
        LLMToolConfig(tool_class=ProductSQLSearchTool),
        LLMToolConfig(tool_class=PlaceOrderTool),
    ]
    FILE_UPLOAD = True
