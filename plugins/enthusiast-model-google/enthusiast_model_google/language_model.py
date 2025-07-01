from enthusiast_common.registry.llm import LanguageModelProvider
from enthusiast_common.utils import prioritize_items
from google import genai
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.language_models import BaseLanguageModel
from langchain_google_genai import ChatGoogleGenerativeAI

PRIORITIZED_MODELS = ["models/gemini-2.0-flash", "models/gemini-1.5-flash"]


class GoogleLanguageModelProvider(LanguageModelProvider):
    STREAMING_AVAILABLE = False

    def provide_language_model(self, callbacks: list[BaseCallbackHandler] | None = None) -> BaseLanguageModel:
        return ChatGoogleGenerativeAI(model=self._model)

    def model_name(self) -> str:
        return self._model

    @staticmethod
    def available_models() -> list[str]:
        all_models = genai.Client().models.list()
        gemini_models = [model.name for model in all_models if "generateContent" in model.supported_actions]
        return prioritize_items(gemini_models, PRIORITIZED_MODELS)
