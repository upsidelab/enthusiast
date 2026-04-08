from enthusiast_common.registry.llm import LanguageModelProvider
from enthusiast_common.structures import BaseContent, LLMFile
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.language_models import BaseLanguageModel
from langchain_ollama import ChatOllama
from ollama import Client

from .embedding import OllamaEmbeddingProvider


class OllamaImageContent(BaseContent):
    type: str = "image_url"
    image_url: str


class OllamaFileContent(BaseContent):
    type: str = "document_url"
    document_url: str


class OllamaLanguageModelProvider(LanguageModelProvider):
    NAME = "Ollama"
    STREAMING_AVAILABLE = False

    def provide_language_model(self, callbacks: list[BaseCallbackHandler] | None = None) -> BaseLanguageModel:
        return ChatOllama(model=self._model)

    def model_name(self) -> str:
        return self._model

    @staticmethod
    def available_models() -> list[str]:
        all_model_names = map(lambda m: m.model, Client().list().models)
        llm_models = [
            model_name for model_name in all_model_names
                        if model_name and not OllamaEmbeddingProvider.is_embedding_model(model_name)
        ]
        return llm_models

    @staticmethod
    def prepare_image_object(file_object: LLMFile) -> OllamaImageContent:
        image_url = f"data:{file_object.content_type};base64,{file_object.content}"
        return OllamaImageContent(image_url=image_url)

    @staticmethod
    def prepare_file_object(file_object: LLMFile) -> OllamaFileContent:
        document_url = f"data:{file_object.content_type};base64,{file_object.content}"
        return OllamaFileContent(document_url=document_url)
