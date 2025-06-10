from enthusiast_common import LanguageModelProvider
from enthusiast_common.utils import prioritize_items
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.language_models import BaseLanguageModel
from langchain_openai import ChatOpenAI
from openai import OpenAI


PRIORITIZED_MODELS = ["gpt-4o", "gpt-4o-mini"]


class OpenAILanguageModelProvider(LanguageModelProvider):
    def provide_language_model(self) -> BaseLanguageModel:
        return ChatOpenAI(model=self._model)

    def provide_streaming_language_model(self, callbacks: list[BaseCallbackHandler] | None) -> BaseLanguageModel:
        return ChatOpenAI(model=self._model, callbacks=callbacks, streaming=True)

    def model_name(self) -> str:
        return self._model

    @staticmethod
    def available_models() -> list[str]:
        all_models = OpenAI().models.list().data
        gpt_models = [model.id for model in all_models if model.id.startswith("gpt-")]
        return prioritize_items(gpt_models, PRIORITIZED_MODELS)
