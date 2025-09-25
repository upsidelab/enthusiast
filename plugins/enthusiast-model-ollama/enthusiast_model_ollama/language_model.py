from typing import Callable

from enthusiast_common.config.prompts import BaseContent
from enthusiast_common.registry.llm import LanguageModelProvider
from enthusiast_common.structures import LLMFile
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.language_models import BaseLanguageModel
from langchain_ollama import ChatOllama
from ollama import Client
from pydantic import ConfigDict


class OllamaFileObject(BaseContent):
    model_config = ConfigDict(extra="allow")


class OllamaPrepareFileMapper:
    @staticmethod
    def gpt_image(file_object: LLMFile) -> OllamaFileObject:
        image_url = f'data:{file_object.content_type};base64,"{file_object.content}"'
        return OllamaFileObject(
            type="input_image",
            image_url=image_url,
        )

    @staticmethod
    def gpt_file(file_object: LLMFile) -> OllamaFileObject:
        file_data = file_object.content
        return OllamaFileObject(
            type="input_file",
            file_data=file_data,
            filename=file_object.filename,
        )

    @staticmethod
    def mistral_image(file_object: LLMFile) -> OllamaFileObject:
        image_url = f"data:{file_object.content_type};base64,{file_object.content}"
        return OllamaFileObject(
            type="image_url",
            image_url=image_url,
        )

    @staticmethod
    def mistral_file(file_object: LLMFile) -> OllamaFileObject:
        document_url = f"data:{file_object.content_type};base64,{file_object.content}"
        return OllamaFileObject(
            type="document_url",
            document_url=document_url,
        )

    @staticmethod
    def gemini_image(file_object: LLMFile) -> OllamaFileObject:
        image_url = f"data:{file_object.content_type};base64,{file_object.content}"
        return OllamaFileObject(
            type="image_url",
            image_url=image_url,
        )

    @staticmethod
    def gemini_file(file_object: LLMFile) -> OllamaFileObject:
        data = file_object.content
        return OllamaFileObject(
            type="input_file",
            data=data,
            mime_type=file_object.content_type,
        )

    MODEL_MAPPING: dict[str, dict[str, Callable[[LLMFile], OllamaFileObject]]] = {
        "gpt": {
            "image": gpt_image.__func__,
            "file": gpt_file.__func__,
        },
        "mistral": {
            "image": mistral_image.__func__,
            "file": mistral_file.__func__,
        },
        "models/gemini": {
            "image": gemini_image.__func__,
            "file": gemini_file.__func__,
        },
    }

    def get_prepare_file_function(self, model: str, file_type: str) -> Callable[[LLMFile], OllamaFileObject]:
        model_object = self.MODEL_MAPPING.get(model)
        if not model_object:
            raise ValueError(f"Model {model} not supported.")
        prepare_file_function = model_object.get(file_type)
        if not prepare_file_function:
            raise ValueError(f"Invalid file type {file_type} for model {model}.")
        return prepare_file_function


class OllamaLanguageModelProvider(LanguageModelProvider):
    STREAMING_AVAILABLE = False
    MODEL_MAPPING_CLASS = OllamaPrepareFileMapper

    def provide_language_model(self, callbacks: list[BaseCallbackHandler] | None = None) -> BaseLanguageModel:
        return ChatOllama(model=self._model)

    def model_name(self) -> str:
        return self._model

    @staticmethod
    def available_models() -> list[str]:
        ollama_client = Client()
        return [model.model for model in ollama_client.list().models]

    def prepare_image_object(self, file_object: LLMFile) -> OllamaFileObject:
        return self.MODEL_MAPPING_CLASS().get_prepare_file_function(model=self._model, file_type="image")(file_object)

    def prepare_file_object(self, file_object: LLMFile) -> OllamaFileObject:
        return self.MODEL_MAPPING_CLASS().get_prepare_file_function(model=self._model, file_type="file")(file_object)
