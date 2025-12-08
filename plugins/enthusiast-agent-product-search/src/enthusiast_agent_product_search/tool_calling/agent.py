from enthusiast_agent_tool_calling import BaseToolCallingAgent
from enthusiast_common.config.base import LLMToolConfig

from ..tools.product_search_tool import ProductSearchTool


class ProductSearchToolCallingAgent(BaseToolCallingAgent):
    TOOLS = [
        LLMToolConfig(tool_class=ProductSearchTool),
    ]
