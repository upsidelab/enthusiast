from enthusiast_agent_tool_calling import BaseToolCallingAgent
from enthusiast_common.config.base import LLMToolConfig

from .tools import RetrieveDocumentsTool
from .tools import VerifySolutionTool


class UserManualSearchToolCallingAgent(BaseToolCallingAgent):
    AGENT_KEY = "enthusiast-agent-user-manual-search"
    NAME = "User Manual Search"
    TOOLS = [
        LLMToolConfig(tool_class=VerifySolutionTool),
        LLMToolConfig(tool_class=RetrieveDocumentsTool)
    ]
