from abc import abstractmethod, ABC
from typing import Type, Any

from langchain.agents import AgentExecutor
from langchain_core.language_models import BaseLanguageModel
from langchain_core.tools import BaseTool
from pydantic import BaseModel


class AbstractTool(BaseTool, ABC):
    pass


class BaseFunctionTool(AbstractTool):
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


class BaseLLMTool(AbstractTool):
    name: str
    description: str
    args_schema: Type[BaseModel]
    return_direct: bool
    data_set: any

    def __init__(
        self,
        data_set: Any,
        llm: BaseLanguageModel,
        **kwargs,
    ):
        """Initialize the ToolInterface.

        Args:
            language_model_provider (LanguageModelProvider): A language model provider that the tool can use.
            **kwargs: Additional keyword arguments.
        """

        super().__init__(**kwargs)
        self.data_set = data_set
        self.llm = llm

    @abstractmethod
    def _run(self, *args, **kwargs):
        """Abstract method to run the tool.

        Args:
            *args: Positional arguments.
            **kwargs: Keyword arguments.
        """
        pass


class BaseAgentTool(AbstractTool):
    name: str
    description: str
    args_schema: Type[BaseModel]
    return_direct: bool
    agent_executor: AgentExecutor

    def __init__(self, agent_executor: AgentExecutor, **kwargs):
        """Initialize the ToolInterface.

        Args:
            agent_executor (AgentExecutor): Agent executor to invoke LLM.
            **kwargs: Additional keyword arguments.
        """
        super().__init__(**kwargs)
        self.agent_executor = agent_executor

    @abstractmethod
    def _run(self, *args, **kwargs):
        """Abstract method to run the tool.

        Args:
            *args: Positional arguments.
            **kwargs: Keyword arguments.
        """
        pass
