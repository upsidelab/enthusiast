from enthusiast_agent_tool_calling import BaseToolCallingAgent
from enthusiast_common.config.base import LLMToolConfig

from ..tools.place_order_tool import OrderPlacementTool
from ..tools.product_search_tool import ProductSearchTool


class OCROrderToolCallingAgent(BaseToolCallingAgent):
    TOOLS = [
        LLMToolConfig(tool_class=ProductSearchTool),
        LLMToolConfig(tool_class=OrderPlacementTool),
    ]
    FILE_UPLOAD = True
