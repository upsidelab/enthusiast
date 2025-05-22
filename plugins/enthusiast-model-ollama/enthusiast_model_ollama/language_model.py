from enthusiast_common.interfaces import LanguageModelProvider
from langchain_core.language_models import BaseLanguageModel
from langchain_ollama import ChatOllama
from ollama import Client


class OllamaLanguageModelProvider(LanguageModelProvider):
    def provide_language_model(self) -> BaseLanguageModel:
        return ChatOllama(model=self._model)

    def model_name(self) -> str:
        return self._model

    @staticmethod
    def available_models() -> list[str]:
        ollama_client = Client()
        return [model.model for model in ollama_client.list().models]
