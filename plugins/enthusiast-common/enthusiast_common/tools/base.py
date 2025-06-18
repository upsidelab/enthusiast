from abc import abstractmethod
from typing import Type

from enthusiast_common.agents import BaseAgent
from enthusiast_common.repositories import BaseDataSetRepository
from langchain_core.language_models import BaseLanguageModel
from langchain_core.tools import BaseTool
from pydantic import BaseModel

from ..injectors import BaseInjector


class BaseFunctionTool(BaseTool):
    name: str
    description: str
    args_schema: Type[BaseModel]
    return_direct: bool

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @abstractmethod
    def _run(self, *args, **kwargs):
        """Abstract method to run the tool.

        Args:
            *args: Positional arguments.
            **kwargs: Keyword arguments.
        """
        pass


class BaseLLMTool(BaseTool):
    name: str
    description: str
    args_schema: Type[BaseModel]
    return_direct: bool
    data_set_id: int
    injector: BaseInjector | None

    def __init__(
        self,
        data_set_id: int,
        data_set_repo: BaseDataSetRepository,
        llm: BaseLanguageModel,
        injector: BaseInjector | None,
        **kwargs,
    ):
        """Initialize the ToolInterface.

        Args:
            language_model_provider (LanguageModelProvider): A language model provider that the tool can use.
            **kwargs: Additional keyword arguments.
        """

        super().__init__(**kwargs)
        self.injector = injector
        self.data_set_repo = data_set_repo
        self.llm = llm
        self.data_set_id = data_set_id

    @abstractmethod
    def _run(self, *args, **kwargs):
        """Abstract method to run the tool.

        Args:
            *args: Positional arguments.
            **kwargs: Keyword arguments.
        """
        pass


class BaseAgentTool(BaseTool):
    name: str
    description: str
    args_schema: Type[BaseModel]
    return_direct: bool
    agent: BaseAgent

    def __init__(self, agent: BaseAgent, injector: BaseInjector | None, **kwargs):
        """Initialize the ToolInterface.

        Args:
            agent_executor (AgentExecutor): Agent executor to invoke LLM.
            **kwargs: Additional keyword arguments.
        """
        super().__init__(**kwargs)
        self.agent = agent
        self.injector = injector

    @abstractmethod
    def _run(self, *args, **kwargs):
        """Abstract method to run the tool.

        Args:
            *args: Positional arguments.
            **kwargs: Keyword arguments.
        """
        pass
