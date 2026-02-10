from enthusiast_agent_tool_calling import BaseToolCallingAgent
from enthusiast_common.config.base import LLMToolConfig
from enthusiast_agent_product_search.tools import ProductExamplesTool, ProductSQLSearchTool

from .tools.place_order_tool import PlaceOrderTool


class OCRToOrderAgent(BaseToolCallingAgent):
    AGENT_KEY = "enthusiast-agent-ocr-to-order"
    NAME = "Purchase Order OCR"
    TOOLS = [
        LLMToolConfig(tool_class=ProductExamplesTool),
        LLMToolConfig(tool_class=ProductSQLSearchTool),
        LLMToolConfig(tool_class=PlaceOrderTool),
    ]
    FILE_UPLOAD = True
