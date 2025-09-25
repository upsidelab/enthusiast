from enthusiast_common.config.prompts import BaseContent
from enthusiast_common.registry.llm import LanguageModelProvider
from enthusiast_common.structures import LLMFile
from enthusiast_common.utils import prioritize_items
from google import genai
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.language_models import BaseLanguageModel
from langchain_google_genai import ChatGoogleGenerativeAI

PRIORITIZED_MODELS = ["models/gemini-2.0-flash", "models/gemini-1.5-flash"]


class GoogleAIImageContent(BaseContent):
    image_url: str


class GoogleAIFileContent(BaseContent):
    mime_type: str
    data: str


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

    @staticmethod
    def prepare_image_object(file_object: LLMFile, data_placeholder: bool = True) -> GoogleAIImageContent:
        if data_placeholder:
            image_url = (
                f"data:{file_object.content_type};base64,{{{LanguageModelProvider.FILE_KEY_PREFIX}{file_object.id}}}"
            )
        else:
            image_url = f"data:{file_object.content_type};base64,{file_object.content}"
        return GoogleAIImageContent(
            type="image_url",
            image_url=image_url,
        )

    @staticmethod
    def prepare_file_object(file_object: LLMFile, data_placeholder: bool = True) -> GoogleAIFileContent:
        if data_placeholder:
            data = f"{LanguageModelProvider.FILE_KEY_PREFIX}{file_object.id}"
        else:
            data = file_object.content
        return GoogleAIFileContent(type="input_file", data=data, mime_type=file_object.content_type)
