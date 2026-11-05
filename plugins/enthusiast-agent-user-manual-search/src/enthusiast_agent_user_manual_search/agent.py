from enthusiast_vertical.builder import EcommerceAgentBuilder
from suvereo_agent_tool_calling import BaseToolCallingAgent
from suvereo_common.config.base import LLMToolConfig

from .prompt import USER_MANUAL_TOOL_CALLING_AGENT_PROMPT
from .tools import RetrieveDocumentsTool, VerifySolutionTool


class UserManualSearchAgent(BaseToolCallingAgent):
    AGENT_KEY = "enthusiast-agent-user-manual-search"
    NAME = "User Manual Search"
    SYSTEM_PROMPT = USER_MANUAL_TOOL_CALLING_AGENT_PROMPT
    BUILDER_CLASS = EcommerceAgentBuilder
    TOOLS = [
        LLMToolConfig(tool_class=VerifySolutionTool),
        LLMToolConfig(tool_class=RetrieveDocumentsTool)
    ]
