from enthusiast_common.agents import BaseAgent
from enthusiast_common.config.base import LLMToolConfig
from enthusiast_common.config.prompts import ChatPromptTemplateConfig
from enthusiast_common.structures import LLMFile
from enthusiast_common.tools.base import BaseTool
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.language_models import BaseLanguageModel

from agent.core.injector import Injector
from agent.core.registries.language_models import LanguageModelRegistry
from agent.core.tools import CreateAnswerTool


class ToolCallingAgent(BaseAgent):
    AGENT_ARGS = None
    PROMPT_INPUT = None
    PROMPT_EXTENSION = None
    TOOLS = [LLMToolConfig(tool_class=CreateAnswerTool)]

    def __init__(
        self,
        tools: list[BaseTool],
        llm: BaseLanguageModel,
        prompt: ChatPromptTemplateConfig,
        conversation_id: int,
        injector: Injector,
        callback_handler: BaseCallbackHandler | None = None,
    ):
        self._tools = tools
        self._llm = llm
        self._prompt = prompt
        self._injector = injector
        self._conversation_id = conversation_id
        self._callback_handler = callback_handler
        super().__init__(
            tools=tools,
            llm=llm,
            prompt=prompt,
            conversation_id=conversation_id,
            callback_handler=callback_handler,
            injector=injector,
        )

    def _create_agent_executor(self, files_content: list[LLMFile]) -> AgentExecutor:
        tools = self._create_tools()
        prompt = self._create_prompt(files_content)
        agent = create_tool_calling_agent(self._llm, tools, prompt)
        return AgentExecutor(agent=agent, tools=tools, verbose=True, memory=self._injector.chat_summary_memory)

    def _create_tools(self):
        return [tool_class.as_tool() for tool_class in self._tools]

    def get_answer(self, input_text: str, files_content: list[LLMFile]) -> str:
        agent_executor = self._create_agent_executor(files_content)
        agent_output = agent_executor.invoke(
            {"input": input_text}, config={"callbacks": [self._callback_handler] if self._callback_handler else []}
        )
        return agent_output["output"]

    def _create_prompt(self, files_content: list[LLMFile]):
        data_set_id = self._injector.repositories.conversation.get_data_set_id(self._conversation_id)
        llm_provider = LanguageModelRegistry(self._injector.repositories.data_set).provider_for_dataset(data_set_id)
        files_objects = llm_provider.prepare_files_objects(files_objects=files_content)
        file_injected_prompt = self._prompt.add_files_content(files_objects)
        return file_injected_prompt.to_chat_prompt_template()
