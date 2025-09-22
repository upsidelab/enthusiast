from enthusiast_common.config.prompts import BaseContent
from enthusiast_common.registry.llm import LanguageModelProvider
from enthusiast_common.structures import LLMFile
from enthusiast_common.utils import prioritize_items
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.language_models import BaseLanguageModel
from langchain_openai import ChatOpenAI
from openai import OpenAI

PRIORITIZED_MODELS = ["gpt-4o", "gpt-4.1", "gpt-4o-mini", "gpt-4.1-mini"]


class OpenAIImageContent(BaseContent):
    image_url: str


class OpenAIFileContent(BaseContent):
    filename: str
    file_data: str


class OpenAILanguageModelProvider(LanguageModelProvider):
    def provide_language_model(self, callbacks: list[BaseCallbackHandler] | None = None) -> BaseLanguageModel:
        return ChatOpenAI(model=self._model, callbacks=callbacks)

    def provide_streaming_language_model(self, callbacks: list[BaseCallbackHandler] | None) -> BaseLanguageModel:
        return ChatOpenAI(model=self._model, callbacks=callbacks, streaming=True)

    def model_name(self) -> str:
        return self._model

    @staticmethod
    def available_models() -> list[str]:
        all_models = OpenAI().models.list().data
        gpt_models = [model.id for model in all_models if model.id.startswith("gpt-")]
        return prioritize_items(gpt_models, PRIORITIZED_MODELS)

    @staticmethod
    def prepare_image_object(file_object: LLMFile, data_placeholder: bool = True) -> OpenAIImageContent:
        if data_placeholder:
            image_url = (
                f'data:{file_object.content_type};base64,"{{{LanguageModelProvider.FILE_KEY_PREFIX}{file_object.id}}}"'
            )
        else:
            image_url = f'data:{file_object.content_type};base64,"{file_object.content}"'
        return OpenAIImageContent(
            type="input_image",
            image_url=image_url,
        )

    @staticmethod
    def prepare_file_object(file_object: LLMFile, data_placeholder: bool = True) -> OpenAIFileContent:
        if data_placeholder:
            file_data = f'"{{{LanguageModelProvider.FILE_KEY_PREFIX}{file_object.id}}}"'
        else:
            file_data = file_object.content
        return OpenAIFileContent(
            type="input_file",
            file_data=file_data,
            filename=file_object.filename,
        )
