from abc import ABC, ABCMeta, abstractmethod
from typing import Any

from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.language_models import BaseLanguageModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import BaseTool

from enthusiast_common.injectors import BaseInjector

from ..utils import NoUnionOptionalModel, validate_required_vars


class ExtraArgsClassBaseMeta(ABCMeta):
    REQUIRED_VARS = {
        "AGENT_ARGS": NoUnionOptionalModel,
        "PROMPT_INPUT_SCHEMA": NoUnionOptionalModel,
        "PROMPT_EXTENSION": NoUnionOptionalModel,
        "TOOLS": list[BaseTool],
    }

    def __new__(mcs, name, bases, namespace, **kwargs):
        cls = super().__new__(mcs, name, bases, namespace, **kwargs)
        if not namespace.get("__abstract__", False):
            return validate_required_vars(cls, name, cls.REQUIRED_VARS)
        return cls


class ExtraArgsClassBase(metaclass=ExtraArgsClassBaseMeta):
    __abstract__ = True


class BaseAgent(ABC, ExtraArgsClassBase):
    def __init__(
        self,
        tools: list[BaseTool],
        llm: BaseLanguageModel,
        prompt: ChatPromptTemplate,
        conversation_id: Any,
        injector: BaseInjector,
        callback_handler: BaseCallbackHandler | None = None,
    ):
        self._tools = tools
        self._llm = llm
        self._prompt = prompt
        self._conversation_id = conversation_id
        self._callback_handler = callback_handler
        self._injector = injector

    @abstractmethod
    def get_answer(self, input_text: str) -> str:
        pass
