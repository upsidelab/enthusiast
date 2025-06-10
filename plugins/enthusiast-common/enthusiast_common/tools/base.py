from abc import abstractmethod, ABC
from typing import Type

from langchain_core.tools import BaseTool
from pydantic import BaseModel

from ..interfaces import LanguageModelProvider


class AbstractTool(BaseTool, ABC):
    @classmethod
    @abstractmethod
    def create(cls, *args, **kwargs):
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

    def create(cls, *args, **kwargs):
        return cls()


class BaseLLMTool(BaseTool):
    name: str
    description: str
    args_schema: Type[BaseModel]
    return_direct: bool

    def __init__(
        self,
        data_set,
        chat_model,
        language_model_provider: LanguageModelProvider,
        **kwargs,
    ):
        """Initialize the ToolInterface.

        Args:
            language_model_provider (LanguageModelProvider): A language model provider that the tool can use.
            **kwargs: Additional keyword arguments.
        """

        super().__init__(**kwargs)
        self.data_set = data_set
        self.chat_model = chat_model
        self._language_model_provider = language_model_provider

    @abstractmethod
    def _run(self, *args, **kwargs):
        """Abstract method to run the tool.

        Args:
            *args: Positional arguments.
            **kwargs: Keyword arguments.
        """
        pass


# class BaseFunctionTool(BaseTool):
#     name: str
#     description: str
#     args_schema: Type[BaseModel]
#     return_direct: bool
#     data_set: any  # TODO use a proper type definition
#     chat_model: Optional[str]
#
#     def __init__(
#         self,
#         data_set,
#         chat_model,
#         language_model_provider: LanguageModelProvider,
#         **kwargs,
#     ):
#         """Initialize the ToolInterface.
#
#         Args:
#             data_set (Any): The dataset used by the tool.
#             chat_model (str, deprecated): This param is deprecated and will be removed in future versions. Use `language_model_provider.model_name()` instead.
#             language_model_provider (LanguageModelProvider): A language model provider that the tool can use.
#             **kwargs: Additional keyword arguments.
#         """
#         super(CustomTool, self).__init__(**kwargs)
#         self.data_set = data_set
#         self.chat_model = chat_model
#         self._language_model_provider = language_model_provider
#
#     @abstractmethod
#     def _run(self, *args, **kwargs):
#         """Abstract method to run the tool.
#
#         Args:
#             *args: Positional arguments.
#             **kwargs: Keyword arguments.
#         """
#         pass
