from enthusiast_agent_tool_calling import BaseToolCallingAgent
from enthusiast_common.config.base import LLMToolConfig

from ..tools.document_retriver_tool import RetrieveDocumentsTool
from ..tools.solution_verification_tool import SolutionVerificationTool


class UserManualSearchToolCallingAgent(BaseToolCallingAgent):
    TOOLS = [LLMToolConfig(tool_class=SolutionVerificationTool), LLMToolConfig(tool_class=RetrieveDocumentsTool)]
