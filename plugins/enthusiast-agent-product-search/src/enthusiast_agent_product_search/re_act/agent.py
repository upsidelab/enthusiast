from enthusiast_agent_re_act import BaseReActAgent
from enthusiast_common.config.base import LLMToolConfig

from ..tools import PresentProductsTool, ProductSearchTool


class ProductSearchReActAgent(BaseReActAgent):
    TOOLS = [
        LLMToolConfig(tool_class=ProductSearchTool),
        LLMToolConfig(tool_class=PresentProductsTool),
    ]
