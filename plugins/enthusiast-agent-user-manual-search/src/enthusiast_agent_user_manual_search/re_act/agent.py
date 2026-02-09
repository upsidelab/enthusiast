from enthusiast_agent_re_act import BaseReActAgent, StructuredReActOutputParser
from enthusiast_common.config.base import LLMToolConfig
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.tools import render_text_description_and_args

from ..tools import RetrieveDocumentsTool
from ..tools import VerifySolutionTool


class UserManualSearchAgent(BaseReActAgent):
    AGENT_KEY = "enthusiast-agent-user-manual-search"
    NAME = "User Manual Search"
    TOOLS = [LLMToolConfig(tool_class=VerifySolutionTool), LLMToolConfig(tool_class=RetrieveDocumentsTool)]

    def get_answer(self, input_text: str) -> str:
        agent_executor = self._build_agent_executor()
        response = agent_executor.invoke({"input": input_text}, config=self._build_invoke_config())
        return response["output"]
