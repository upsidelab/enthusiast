from enthusiast_agent_re_act import BaseReActAgent, StructuredReActOutputParser
from enthusiast_common.config.base import LLMToolConfig
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.tools import render_text_description_and_args

from ..tools.product_search_tool import ProductSearchTool


class ProductSearchReActAgent(BaseReActAgent):
    AGENT_KEY = "enthusiast-agent-product-search"
    NAME = "Product Search"
    TOOLS = [
        LLMToolConfig(tool_class=ProductSearchTool),
    ]
