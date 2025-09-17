from abc import ABC, ABCMeta, abstractmethod
from typing import Any

from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.language_models import BaseLanguageModel
from langchain_core.tools import BaseTool
from pydantic import BaseModel

from ..config.prompts import ChatPromptTemplateConfig
from ..injectors import BaseInjector
from ..registry import BaseLanguageModelRegistry
from ..structures import LLMFile
from ..utils import RequiredFieldsModel, validate_required_vars


class ExtraArgsClassBaseMeta(ABCMeta):
    REQUIRED_VARS = {
        "AGENT_ARGS": RequiredFieldsModel,
        "PROMPT_INPUT": RequiredFieldsModel,
        "PROMPT_EXTENSION": RequiredFieldsModel,
        "TOOLS": list[BaseModel],
    }

    def __new__(mcs, name, bases, namespace, **kwargs):
        cls = super().__new__(mcs, name, bases, namespace, **kwargs)
        if not namespace.get("__abstract__", False):
            return validate_required_vars(cls, name, cls.REQUIRED_VARS)
        return cls


class ExtraArgsClassBase(metaclass=ExtraArgsClassBaseMeta):
    __abstract__ = True


class BaseAgent(ABC, ExtraArgsClassBase):
    AGENT_ARGS = None
    PROMPT_INPUT = None
    PROMPT_EXTENSION = None
    TOOLS = []

    def __init__(
        self,
        tools: list[BaseTool],
        llm: BaseLanguageModel,
        llm_registry: BaseLanguageModelRegistry,
        prompt: ChatPromptTemplateConfig,
        conversation_id: Any,
        injector: BaseInjector,
        callback_handler: BaseCallbackHandler | None = None,
    ):
        self._tools = tools
        self._llm = llm
        self._llm_registry = llm_registry
        self._prompt = prompt
        self._conversation_id = conversation_id
        self._callback_handler = callback_handler
        self._injector = injector

    @abstractmethod
    def get_answer(self, input_text: str, files_content: list[LLMFile]) -> str:
        pass

    def set_runtime_arguments(self, runtime_arguments: Any) -> None:
        tools_runtime_arguments = runtime_arguments.pop("tools")
        for key, value in runtime_arguments.items():
            class_field_key = key.upper()
            field = getattr(self, class_field_key)
            if field is None:
                continue
            setattr(self, key.upper(), field(**value))
        for index, tool in enumerate(self._tools):
            tool.set_runtime_arguments(tools_runtime_arguments[index])

    def _create_prompt(self, files_content: list[LLMFile]):
        data_set_id = self._injector.repositories.conversation.get_data_set_id(self._conversation_id)
        llm_provider = self._llm_registry.provider_for_dataset(data_set_id)
        files_objects = llm_provider.prepare_files_objects(files_objects=files_content)
        file_injected_prompt = self._prompt.add_files_content(files_objects)
        return file_injected_prompt.to_chat_prompt_template()
