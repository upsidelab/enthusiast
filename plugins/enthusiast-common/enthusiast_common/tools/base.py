import inspect
from abc import ABC, ABCMeta, abstractmethod
from typing import Any, Type

from enthusiast_common.agents import BaseAgent
from enthusiast_common.repositories import BaseDataSetRepository
from langchain_core.language_models import BaseLanguageModel
from langchain_core.tools import Tool
from pydantic import BaseModel

from ..injectors import BaseInjector


class ToolMeta(ABCMeta):
    REQUIRED_CLASS_VARS = {
        "NAME": str,
        "DESCRIPTION": str,
        "ARGS_SCHEMA": type,
        "RETURN_DIRECT": bool,
    }

    def __new__(mcs, name, bases, namespace, **kwargs):
        cls = super().__new__(mcs, name, bases, namespace, **kwargs)

        if inspect.isabstract(cls):
            return cls

        for var_name, expected_type in mcs.REQUIRED_CLASS_VARS.items():
            if not hasattr(cls, var_name):
                raise TypeError(f"Class '{name}' must define class variable '{var_name}'")
            value = getattr(cls, var_name)
            if not isinstance(value, expected_type):
                raise TypeError(
                    f"Class variable '{var_name}' in '{name}' must be of type {expected_type.__name__}, "
                    f"but got {type(value).__name__}"
                )
        return cls


class BaseTool(metaclass=ToolMeta):
    NAME: str
    DESCRIPTION: str
    ARGS_SCHEMA: Type[BaseModel]
    RETURN_DIRECT: bool

    REQUIRED_CLASS_VARS = {
        "NAME": str,
        "DESCRIPTION": str,
        "ARGS_SCHEMA": type,
        "RETURN_DIRECT": bool,
    }

    @abstractmethod
    def run(self, *args, **kwargs):
        pass

    def as_tool(self) -> Tool:
        return Tool.from_function(
            func=self.run,
            name=self.NAME,
            description=self.DESCRIPTION,
            args_schema=self.ARGS_SCHEMA,
            return_direct=self.RETURN_DIRECT,
        )


class BaseFunctionTool(BaseTool, ABC):
    pass


class BaseLLMTool(BaseTool, ABC):
    def __init__(
        self,
        data_set_id: Any,
        data_set_repo: BaseDataSetRepository,
        llm: BaseLanguageModel,
        injector: BaseInjector | None,
    ):
        self._data_set_id = data_set_id
        self._data_set_repo = data_set_repo
        self._llm = llm
        self._injector = injector


class BaseAgentTool(BaseTool, ABC):
    def __init__(self, agent: BaseAgent):
        self._agent = agent
