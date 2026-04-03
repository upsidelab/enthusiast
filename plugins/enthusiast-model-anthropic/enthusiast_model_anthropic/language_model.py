from anthropic import Anthropic
from enthusiast_common.registry.llm import LanguageModelProvider
from enthusiast_common.structures import BaseContent, LLMFile
from enthusiast_common.utils import prioritize_items
from langchain_anthropic import ChatAnthropic
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.language_models import BaseLanguageModel
from pydantic import BaseModel

PRIORITIZED_MODELS = ["claude-opus-4-6", "claude-sonnet-4-6"]


class AnthropicImageSource(BaseModel):
    type: str
    media_type: str
    data: str


class AnthropicImageContent(BaseContent):
    source: AnthropicImageSource


class AnthropicDocumentSource(BaseModel):
    type: str
    media_type: str
    data: str


class AnthropicDocumentContent(BaseContent):
    source: AnthropicDocumentSource


class AnthropicLanguageModelProvider(LanguageModelProvider):

    NAME = "Anthropic"
    STREAMING_REQUIRES_MESSAGE_BUFFERING = True

    def provide_language_model(self, callbacks: list[BaseCallbackHandler] | None = None) -> BaseLanguageModel:
        return ChatAnthropic(model=self._model, callbacks=callbacks)

    def provide_streaming_language_model(self, callbacks: list[BaseCallbackHandler] | None = None) -> BaseLanguageModel:
        return ChatAnthropic(model=self._model, callbacks=callbacks, streaming=True)

    def model_name(self) -> str:
        return self._model

    @staticmethod
    def available_models() -> list[str]:
        all_models = Anthropic().models.list().data
        model_ids = [model.id for model in all_models]
        return prioritize_items(model_ids, PRIORITIZED_MODELS)

    @staticmethod
    def prepare_image_object(file_object: LLMFile) -> AnthropicImageContent:
        return AnthropicImageContent(
            type="image",
            source=AnthropicImageSource(
                type="base64",
                media_type=file_object.content_type,
                data=file_object.content,
            ),
        )

    @staticmethod
    def prepare_file_object(file_object: LLMFile) -> AnthropicDocumentContent:
        return AnthropicDocumentContent(
            type="document",
            source=AnthropicDocumentSource(
                type="base64",
                media_type=file_object.content_type,
                data=file_object.content,
            ),
        )
