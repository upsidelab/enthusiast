import logging

import tiktoken
from enthusiast_common.injectors import BaseInjector
from enthusiast_common.tools import BaseLLMTool
from langchain_core.language_models import BaseLanguageModel
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class RetrieveDocumentsToolInput(BaseModel):
    full_user_request: str = Field(description="user's full request")


class RetrieveDocumentsTool(BaseLLMTool):
    NAME = "retrieve_documents_tool"
    DESCRIPTION = "Use it to get pieces of user manuals"
    ARGS_SCHEMA = RetrieveDocumentsToolInput
    RETURN_DIRECT = False

    ENCODING: tiktoken.encoding_for_model = None
    MAX_TOKENS: int = 30000

    def __init__(
        self,
        data_set_id: int,
        llm: BaseLanguageModel,
        injector: BaseInjector,
    ):
        super().__init__(data_set_id=data_set_id, llm=llm, injector=injector)
        if llm.name in tiktoken.model.MODEL_TO_ENCODING:
            self.ENCODING = tiktoken.encoding_for_model(llm.name)
        else:
            self.ENCODING = tiktoken.encoding_for_model("gpt-4o")

    def _get_document_context(self, relevant_documents):
        offset = 0.8
        document_context = " ".join(map(lambda x: x.content, relevant_documents[: len(relevant_documents)]))
        tokens_cnt = len(self.ENCODING.encode(document_context))
        if tokens_cnt > self.MAX_TOKENS:
            words_to_remove = round(offset * (tokens_cnt - self.MAX_TOKENS))
            words = document_context.split()
            words = words[: len(words) - words_to_remove]
            document_context = " ".join(words)
        return document_context

    def run(self, full_user_request: str):
        document_retriever = self._injector.document_retriever
        relevant_documents = document_retriever.find_content_matching_query(full_user_request)
        return self._get_document_context(relevant_documents)

    def as_tool(self) -> StructuredTool:
        return StructuredTool.from_function(
            func=self.run,
            name=self.NAME,
            description=self.DESCRIPTION,
            args_schema=self.ARGS_SCHEMA,
            return_direct=self.RETURN_DIRECT,
        )
