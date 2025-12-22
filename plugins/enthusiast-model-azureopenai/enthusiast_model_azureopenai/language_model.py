from enthusiast_common.registry.llm import LanguageModelProvider
from enthusiast_common.structures import BaseContent, LLMFile
from enthusiast_common.utils import prioritize_items
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.language_models import BaseLanguageModel
from langchain_openai import AzureChatOpenAI
from openai import AzureOpenAI
from pydantic import BaseModel

PRIORITIZED_MODELS = ["gpt-4.1", "gpt-4.1-mini", "gpt-5", "gpt-5.2"]


class AzureOpenAIImageContent(BaseContent):
    image_url: str


class AzureOpenAIFileObject(BaseModel):
    filename: str
    file_data: str


class AzureOpenAIFileContent(BaseContent):
    file: AzureOpenAIFileObject


class AzureOpenAILanguageModelProvider(LanguageModelProvider):
    def provide_language_model(self, callbacks: list[BaseCallbackHandler] | None = None) -> BaseLanguageModel:
        return AzureChatOpenAI(model=self._model, callbacks=callbacks)

    def provide_streaming_language_model(self, callbacks: list[BaseCallbackHandler] | None = None, **kwargs) -> BaseLanguageModel:
        return AzureChatOpenAI(model=self._model, callbacks=callbacks, streaming=True)

    def model_name(self) -> str:
        return self._model

    @staticmethod
    def available_models() -> list[str]:
        all_models = AzureOpenAI().models.list().data
        gpt_models = [model.id for model in all_models if model.id.startswith("gpt-")]
        return prioritize_items(gpt_models, PRIORITIZED_MODELS)

    @staticmethod
    def prepare_image_object(file_object: LLMFile) -> AzureOpenAIImageContent:
        image_url = f'data:{file_object.content_type};base64,"{file_object.content}"'
        return AzureOpenAIImageContent(
            type="input_image",
            image_url=image_url,
        )

    @staticmethod
    def prepare_file_object(file_object: LLMFile) -> AzureOpenAIFileContent:
        file_data = f"data:application/pdf;base64,{file_object.content}"
        return AzureOpenAIFileContent(
            type="file", file=AzureOpenAIFileObject(file_data=file_data, filename=file_object.filename)
        )
