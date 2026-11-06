from enthusiast_domain.builder import EcommerceAgentBuilder
from enthusiast_domain_tools import ProductExamplesTool, ProductSQLSearchTool
from suvereo_agent_tool_calling import BaseToolCallingAgent
from suvereo_common.config.base import LLMToolConfig

from .prompt import PRODUCT_SEARCH_TOOL_CALLING_AGENT_PROMPT


class ProductSearchAgent(BaseToolCallingAgent):
    AGENT_KEY = "enthusiast-agent-product-search"
    NAME = "Product Search"
    SYSTEM_PROMPT = PRODUCT_SEARCH_TOOL_CALLING_AGENT_PROMPT
    BUILDER_CLASS = EcommerceAgentBuilder
    TOOLS = [
        LLMToolConfig(tool_class=ProductSQLSearchTool),
        LLMToolConfig(tool_class=ProductExamplesTool),
    ]
