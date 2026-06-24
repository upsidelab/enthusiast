from abc import ABC, ABCMeta, abstractmethod
from typing import Any

from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.language_models import BaseLanguageModel
from langchain_core.tools import BaseTool
from pydantic import BaseModel

from ..injectors import BaseInjector
from ..utils import RequiredFieldsModel, validate_required_vars


class ExtraArgsClassBaseMeta(ABCMeta):
    REQUIRED_VARS = {}

    def __new__(mcs, name, bases, namespace, **kwargs):
        cls = super().__new__(mcs, name, bases, namespace, **kwargs)
        if not namespace.get("__abstract__", False):
            return validate_required_vars(cls, name, cls.REQUIRED_VARS)
        return cls


class AgentExtraArgsClassBaseMeta(ExtraArgsClassBaseMeta):
    REQUIRED_VARS = {
        "AGENT_ARGS": RequiredFieldsModel,
        "PROMPT_INPUT": RequiredFieldsModel,
        "PROMPT_EXTENSION": RequiredFieldsModel,
        "TOOLS": list[BaseModel],
    }


class ExtraArgsClassBase(metaclass=AgentExtraArgsClassBaseMeta):
    __abstract__ = True


class BaseAgent(ABC, ExtraArgsClassBase):
    NAME = None
    AGENT_KEY = None
    AGENT_ARGS = None
    PROMPT_INPUT = None
    PROMPT_EXTENSION = None
    TOOLS = []

    FILE_UPLOAD = False

    def __init__(
        self,
        tools: list[BaseTool],
        llm: BaseLanguageModel,
        system_prompt: str,
        conversation_id: Any,
        injector: BaseInjector,
        callback_handler: BaseCallbackHandler | None = None,
    ):
        self._tools = tools
        self._llm = llm
        self._system_prompt = system_prompt
        self._conversation_id = conversation_id
        self._callback_handler = callback_handler
        self._injector = injector

    @abstractmethod
    def get_answer(self, input_text: str) -> str:
        pass

    def _get_system_prompt_variables(self) -> dict:
        """Return variables to format into the system prompt template."""
        return {}

    def set_runtime_arguments(self, runtime_arguments: Any) -> None:
        """Inject stored config values into agent fields and named tool instances."""
        tool_config = runtime_arguments.get("tool_config", {})
        tool_schema_map = {
            tc.tool_class.NAME: getattr(tc, "tool_configuration_args", None)
            for tc in self.__class__.TOOLS
        }
        for key, value in runtime_arguments.items():
            if key == "tool_config":
                continue
            class_field_key = key.upper()
            field = getattr(self, class_field_key, None)
            if field is None:
                continue
            setattr(self, key.upper(), field(**value))
        for tool in self._tools:
            tool_runtime_args = tool_config.get(tool.NAME)
            if tool_runtime_args is not None:
                schema = tool_schema_map.get(tool.NAME)
                tool.set_runtime_arguments(tool_runtime_args, schema=schema)
