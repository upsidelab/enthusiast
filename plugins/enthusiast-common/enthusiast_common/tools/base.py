import inspect
from abc import ABC, ABCMeta, abstractmethod
from typing import TYPE_CHECKING, Any, Type

if TYPE_CHECKING:
    from ..agents import BaseAgent

from langchain_core.language_models import BaseLanguageModel
from langchain_core.tools import BaseTool as LCBaseTool
from langchain_core.tools import StructuredTool
from pydantic import BaseModel

from ..injectors import BaseInjector
from ..utils import RequiredFieldsModel, validate_required_vars


class ToolMeta(ABCMeta):
    REQUIRED_VARS = {
        "NAME": str,
        "DESCRIPTION": str,
        "ARGS_SCHEMA": type,
        "RETURN_DIRECT": bool,
        "CONFIGURATION_ARGS": RequiredFieldsModel,
    }

    def __new__(mcs, name, bases, namespace, **kwargs):
        cls = super().__new__(mcs, name, bases, namespace, **kwargs)
        if inspect.isabstract(cls):
            return cls
        return validate_required_vars(cls, name, cls.REQUIRED_VARS)


class BaseTool(metaclass=ToolMeta):
    NAME: str
    DESCRIPTION: str
    ARGS_SCHEMA: Type[BaseModel]
    RETURN_DIRECT: bool
    CONFIGURATION_ARGS = None

    REQUIRED_CLASS_VARS = {
        "NAME": str,
        "DESCRIPTION": str,
        "ARGS_SCHEMA": type,
        "RETURN_DIRECT": bool,
        "CONFIGURATION_ARGS": RequiredFieldsModel,
    }

    @abstractmethod
    def run(self, *args, **kwargs):
        pass

    def as_tool(self) -> LCBaseTool:
        return StructuredTool.from_function(
            func=self.run,
            name=self.NAME,
            description=self.DESCRIPTION,
            args_schema=self.ARGS_SCHEMA,
            return_direct=self.RETURN_DIRECT,
        )

    def set_runtime_arguments(self, runtime_arguments: Any) -> None:
        field = getattr(self, "CONFIGURATION_ARGS", None)
        if field is None:
            return
        setattr(self, "CONFIGURATION_ARGS", field(**runtime_arguments))


class BaseFunctionTool(BaseTool, ABC):
    pass


class BaseLLMTool(BaseTool, ABC):
    def __init__(
        self,
        data_set_id: Any,
        llm: BaseLanguageModel,
        injector: BaseInjector,
        conversation_id: Any = None,
    ):
        self._data_set_id = data_set_id
        self._conversation_id = conversation_id
        self._llm = llm
        self._injector = injector


class BaseAgentTool(BaseTool, ABC):
    def __init__(
        self,
        agent: "BaseAgent",  # noqa: F821
    ):
        self._agent = agent
