import os

from enthusiast_common.registry.llm import LanguageModelProvider
from enthusiast_common.structures import BaseContent, LLMFile
from enthusiast_common.utils import prioritize_items
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.language_models import BaseLanguageModel
from langchain_mistralai import ChatMistralAI
from mistralai import Mistral

PRIORITIZED_MODELS = ["mistral-medium-2508", "mistral-medium-2505"]


class MistralAIImageContent(BaseContent):
    image_url: str


class MistralAIFileContent(BaseContent):
    document_url: str


class MistralAILanguageModelProvider(LanguageModelProvider):
    def provide_language_model(self, callbacks: list[BaseCallbackHandler] | None = None) -> BaseLanguageModel:
        return ChatMistralAI(model=self._model, callbacks=callbacks)

    def provide_streaming_language_model(self, callbacks: list[BaseCallbackHandler] | None) -> BaseLanguageModel:
        return ChatMistralAI(model=self._model, callbacks=callbacks, streaming=True)

    def model_name(self) -> str:
        return self._model

    @staticmethod
    def available_models() -> list[str]:
        client = Mistral(api_key=os.environ["MISTRAL_API_KEY"])
        all_models = client.models.list().data
        mistral_models = [model.id for model in all_models if model.id.startswith("mistral-")]
        return prioritize_items(mistral_models, PRIORITIZED_MODELS)

    @staticmethod
    def prepare_image_object(file_object: LLMFile) -> MistralAIImageContent:
        image_url = f"data:{file_object.content_type};base64,{file_object.content}"
        return MistralAIImageContent(
            type="image_url",
            image_url=image_url,
        )

    @staticmethod
    def prepare_file_object(file_object: LLMFile) -> MistralAIFileContent:
        document_url = f"data:{file_object.content_type};base64,{file_object.content}"
        return MistralAIFileContent(
            type="document_url",
            document_url=document_url,
        )
