from enthusiast_agent_re_act import BaseReActAgent, StructuredReActOutputParser
from enthusiast_common.config.base import LLMToolConfig
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.tools import render_text_description_and_args

from .tools.product_search_tool import ProductSearchTool


class ProductSearchReActAgent(BaseReActAgent):
    TOOLS = [
        LLMToolConfig(tool_class=ProductSearchTool),
    ]

    def _build_agent_executor(self) -> AgentExecutor:
        tools = self._build_tools()
        agent = create_react_agent(
            tools=tools,
            llm=self._llm,
            prompt=self._prompt,
            tools_renderer=render_text_description_and_args,
            output_parser=StructuredReActOutputParser(),
        )
        return AgentExecutor(
            agent=agent,
            tools=tools,
            memory=self._build_memory(),
            verbose=True,
            return_intermediate_steps=True,
            handle_parsing_errors=True,
        )

    def get_answer(self, input_text: str) -> str:
        agent_executor = self._build_agent_executor()
        response = agent_executor.invoke({"input": input_text}, config=self._build_invoke_config())
        return response["output"]
