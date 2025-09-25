from enthusiast_common.config.prompts import BaseContent
from enthusiast_common.registry.llm import LanguageModelProvider
from enthusiast_common.structures import LLMFile
from enthusiast_common.utils import prioritize_items
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.language_models import BaseLanguageModel
from langchain_openai import ChatOpenAI
from openai import OpenAI
from pydantic import BaseModel

PRIORITIZED_MODELS = ["gpt-4o", "gpt-4.1", "gpt-4o-mini", "gpt-4.1-mini"]


class OpenAIImageContent(BaseContent):
    image_url: str


class OpenAIFileObject(BaseModel):
    filename: str
    file_data: str


class OpenAIFileContent(BaseContent):
    file: OpenAIFileObject


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
    def prepare_image_object(file_object: LLMFile) -> OpenAIImageContent:
        image_url = f'data:{file_object.content_type};base64,"{file_object.content}"'
        return OpenAIImageContent(
            type="input_image",
            image_url=image_url,
        )

    @staticmethod
    def prepare_file_object(file_object: LLMFile) -> OpenAIFileContent:
        file_data = f"data:application/pdf;base64,{file_object.content}"
        return OpenAIFileContent(type="file", file=OpenAIFileObject(file_data=file_data, filename=file_object.filename))
