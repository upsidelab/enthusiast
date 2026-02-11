from enthusiast_agent_re_act import BaseReActAgent
from enthusiast_common.config.base import LLMToolConfig

from ..tools import PresentProductsTool, ProductSearchTool


class ProductSearchAgent(BaseReActAgent):
    AGENT_KEY = "enthusiast-agent-product-search"
    NAME = "Product Search"
    TOOLS = [
        LLMToolConfig(tool_class=ProductSearchTool),
        LLMToolConfig(tool_class=PresentProductsTool),
    ]
