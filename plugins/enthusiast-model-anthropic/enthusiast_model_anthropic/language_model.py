from anthropic import Anthropic
from enthusiast_common.registry.llm import LanguageModelProvider
from enthusiast_common.structures import BaseContent, LLMFile
from enthusiast_common.utils import prioritize_items
from langchain_anthropic import ChatAnthropic
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.language_models import BaseLanguageModel
from pydantic import BaseModel

PRIORITIZED_MODELS = ["claude-sonnet-4-6", "claude-opus-4-6"]


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
    # Anthropic models support streaming at the API level, but they emit intermediate text tokens
    # before tool calls that are indistinguishable from final-message text tokens. Since our system
    # has no mechanism to filter these out, we treat Anthropic as non-streaming to avoid surfacing
    # partial tool-call preamble to the user.
    STREAMING_AVAILABLE = False

    def provide_language_model(self, callbacks: list[BaseCallbackHandler] | None = None) -> BaseLanguageModel:
        return ChatAnthropic(model=self._model, callbacks=callbacks)

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
