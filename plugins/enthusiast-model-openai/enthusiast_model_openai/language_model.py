from enthusiast_common.interfaces import LanguageModelProvider
from langchain_core.language_models import BaseLanguageModel
from langchain_openai import ChatOpenAI
from openai import OpenAI

from enthusiast_model_openai import utils

PRIORITIZED_MODELS = ["gpt-4o", "gpt-4o-mini"]

class OpenAILanguageModelProvider(LanguageModelProvider):
    def provide_language_model(self) -> BaseLanguageModel:
        return ChatOpenAI(name=self._model)

    @staticmethod
    def available_models() -> list[str]:
        all_models = OpenAI().models.list().data
        gpt_models = [model.id for model in all_models if model.id.startswith("gpt-")]
        return utils.prioritize_items(gpt_models, PRIORITIZED_MODELS)
