from enthusiast_common.interfaces import LanguageModelProvider
from langchain_core.language_models import BaseLanguageModel
from langchain_openai import ChatOpenAI


class OpenAILanguageModelProvider(LanguageModelProvider):
    def provide_language_model(self) -> BaseLanguageModel:
        return ChatOpenAI(name=self._model)
