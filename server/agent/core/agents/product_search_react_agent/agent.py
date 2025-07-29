import logging

from enthusiast_common.agents import BaseAgent
from enthusiast_common.config import LLMToolConfig
from enthusiast_common.utils import RequiredFieldsModel
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.language_models import BaseLanguageModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import BaseTool, render_text_description_and_args
from pydantic import Field

from agent.core.agents.product_search_react_agent.output_parser import CustomReactOutputParser
from agent.core.injector import Injector
from agent.core.tools import ProductsSearchTool, ProductVerificationTool

logger = logging.getLogger(__name__)


class ProductSearchReActAgentInput(RequiredFieldsModel):
    products_type: str = Field(title="Products type", description="Type of product to search for")


class ProductSearchReActAgent(BaseAgent):
    AGENT_ARGS = None
    PROMPT_INPUT = ProductSearchReActAgentInput
    PROMPT_EXTENSION = None
    TOOLS = [LLMToolConfig(tool_class=ProductsSearchTool), LLMToolConfig(tool_class=ProductVerificationTool)]

    def __init__(
        self,
        tools: list[BaseTool],
        llm: BaseLanguageModel,
        prompt: ChatPromptTemplate,
        conversation_id: int,
        injector: Injector,
        callback_handler: BaseCallbackHandler | None = None,
    ):
        self._tools = tools
        self._llm = llm
        self._prompt = prompt
        self._conversation_id = conversation_id
        self._callback_handler = callback_handler
        self._injector = injector
        self._agent_executor = self._create_agent_executor()
        super().__init__(
            tools=tools,
            llm=llm,
            prompt=prompt,
            conversation_id=conversation_id,
            callback_handler=callback_handler,
            injector=injector,
        )

    def _create_agent_executor(self, **kwargs):
        tools = self._create_tools()
        agent = create_react_agent(
            tools=tools,
            llm=self._llm,
            prompt=self._prompt,
            tools_renderer=render_text_description_and_args,
            output_parser=CustomReactOutputParser(),
        )
        return AgentExecutor.from_agent_and_tools(
            agent=agent, tools=tools, verbose=True, memory=self._injector.chat_summary_memory, **kwargs
        )

    def _create_tools(self):
        return [tool_class.as_tool() for tool_class in self._tools]

    def get_answer(self, input_text: str) -> str:
        agent_output = self._agent_executor.invoke(
            {"input": input_text, "products_type": self.PROMPT_INPUT.products_type},
            config={"callbacks": [self._callback_handler] if self._callback_handler else []},
        )
        return agent_output["output"]
