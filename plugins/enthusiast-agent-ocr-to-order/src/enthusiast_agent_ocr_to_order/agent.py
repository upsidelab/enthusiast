from enthusiast_agent_re_act import BaseReActAgent
from enthusiast_common.config.base import LLMToolConfig
from enthusiast_common.registry import LanguageModelProvider
from enthusiast_common.structures import LLMFile
from enthusiast_common.utils import RequiredFieldsModel
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import render_text_description_and_args
from pydantic import Field

from .output_parser import CustomStructuredReActOutputParser
from .tools.order_tool import OrderPlacementTool
from .tools.product_search import ProductSearchTool


class OCRReActAgentInput(RequiredFieldsModel):
    products_type: str = Field(title="Products type", description="Type of product to search for")


class OCRReActAgent(BaseReActAgent):
    TOOLS = [LLMToolConfig(tool_class=ProductSearchTool), LLMToolConfig(tool_class=OrderPlacementTool)]

    def _create_prompt(self, file_objects: list[LLMFile]) -> ChatPromptTemplate:
        data_set_id = self._injector.repositories.conversation.get_data_set_id(self._conversation_id)
        llm_provider = self._llm_registry.provider_for_dataset(data_set_id)
        files_objects = llm_provider.prepare_files_objects(files_objects=file_objects)
        file_injected_prompt = self._prompt.add_files_content(files_objects)
        return file_injected_prompt.to_chat_prompt_template()

    def _prepare_file_inputs(self, file_objects: list[LLMFile]):
        return {
            f"{LanguageModelProvider.FILE_KEY_PREFIX}{file_object.id}": file_object.content
            for file_object in file_objects
        }

    def _build_agent_executor(self, file_objects: list[LLMFile]) -> AgentExecutor:
        tools = self._build_tools()
        prompt = self._create_prompt(file_objects)
        agent = create_react_agent(
            tools=tools,
            llm=self._llm,
            prompt=prompt,
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

    def get_answer(self, input_text: str, file_objects: list[LLMFile]) -> str:
        agent_executor = self._build_agent_executor(file_objects)
        response = agent_executor.invoke(
            {"input": input_text, **self._prepare_file_inputs(file_objects)},
            config=self._build_invoke_config(),
        )
        return response["output"]
