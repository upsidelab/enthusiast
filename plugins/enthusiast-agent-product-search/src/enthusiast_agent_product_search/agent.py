from enthusiast_agent_tool_calling import BaseToolCallingAgent
from enthusiast_common.config.base import LLMToolConfig

from .tools import ProductExamplesTool
from .tools import ProductSQLSearchTool


class ProductSearchToolCallingAgent(BaseToolCallingAgent):
    TOOLS = [
        LLMToolConfig(tool_class=ProductSQLSearchTool),
        LLMToolConfig(tool_class=ProductExamplesTool),
    ]
