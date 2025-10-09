from enthusiast_agent_re_act import BaseReActAgent
from enthusiast_common.config.base import FileToolConfig, LLMToolConfig
from enthusiast_common.tools.files.list_files_tool import FileListTool
from enthusiast_common.tools.files.perform_file_operation_tool import FileRetrievalTool
from enthusiast_common.utils import RequiredFieldsModel
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.tools import render_text_description_and_args
from pydantic import Field

from .output_parser import CustomStructuredReActOutputParser
from .tools.order_tool import OrderPlacementTool
from .tools.product_search import ProductSearchTool


class OCRReActAgentInput(RequiredFieldsModel):
    products_type: str = Field(title="Products type", description="Type of product to search for")


class OCRReActAgent(BaseReActAgent):
    TOOLS = [
        LLMToolConfig(tool_class=ProductSearchTool),
        LLMToolConfig(tool_class=OrderPlacementTool),
        FileToolConfig(tool_class=FileListTool),
        FileToolConfig(tool_class=FileRetrievalTool),
    ]

    def _build_agent_executor(self) -> AgentExecutor:
        tools = self._build_tools()
        agent = create_react_agent(
            tools=tools,
            llm=self._llm,
            prompt=self._prompt,
            tools_renderer=render_text_description_and_args,
            output_parser=CustomStructuredReActOutputParser(),
        )
        return AgentExecutor(
            agent=agent,
            tools=tools,
            memory=self._build_memory(),
            handle_parsing_errors=True,
            verbose=True,
            return_intermediate_steps=True,
        )
