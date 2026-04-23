from enthusiast_agent_product_search.tools import ProductExamplesTool, ProductSQLSearchTool
from enthusiast_agent_tool_calling import BaseToolCallingAgent
from enthusiast_common.config.base import LLMToolConfig

from .tools.place_order_tool import PlaceOrderTool


class OrderIntakeAgent(BaseToolCallingAgent):
    AGENT_KEY = "enthusiast-agent-order-intake"
    NAME = "Order Intake"
    TOOLS = [
        LLMToolConfig(tool_class=ProductExamplesTool),
        LLMToolConfig(tool_class=ProductSQLSearchTool),
        LLMToolConfig(tool_class=PlaceOrderTool),
    ]
    FILE_UPLOAD = True
