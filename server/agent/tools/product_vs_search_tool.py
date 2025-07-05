import logging

import tiktoken
from enthusiast_common.injectors import BaseInjector
from enthusiast_common.tools import BaseLLMTool
from langchain_core.language_models import BaseLanguageModel
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

from agent.repositories import DjangoDataSetRepository

logger = logging.getLogger(__name__)


class ProductVectorStoreSearchInput(BaseModel):
    full_user_request: str = Field(description="user's full request")
    keyword: str = Field(
        description="one-word keyword which will determine an attribute of product for postgres search. It can be color, country, shape"
    )


class ProductVectorStoreSearchTool(BaseLLMTool):
    NAME = "search_matching_products"
    DESCRIPTION = (
        "It's tool for vector store search use it with suitable phrases when you need to find matching products"
    )
    ARGS_SCHEMA = ProductVectorStoreSearchInput
    RETURN_DIRECT = False

    ENCODING: tiktoken.encoding_for_model = None
    MAX_TOKENS: int = 30000
    MAX_RETRY: int = 3

    def __init__(
        self,
        data_set_id: int,
        data_set_repo: DjangoDataSetRepository,
        llm: BaseLanguageModel,
        injector: BaseInjector | None,
    ):
        super().__init__(data_set_id=data_set_id, data_set_repo=data_set_repo, llm=llm, injector=injector)
        self.data_set_id = data_set_id
        self.data_set_repo = data_set_repo
        self.llm = llm
        self.injector = injector
        if llm.name in tiktoken.model.MODEL_TO_ENCODING:
            self.ENCODING = tiktoken.encoding_for_model(llm.name)
        else:
            self.ENCODING = tiktoken.encoding_for_model("gpt-4o")

    def _get_document_context(self, relevant_documents, cut_off_cnt):
        """Identify document context for a query.

        We need to prepare a document context for GPT to provide an answer. If the context is too big, we risk
        exceeding GPT token limit.

        There are two steps to avoid this: 1) remove words which exceed a limit even before sending a query to GPT,
        2) retry loop: if we get the error from GPT (even after removing words), we cut off the whole document.

        1) Remove words over limit (before sending a query to GPT):
        We estimate token number for all the documents with a content that may be relevant to a user's question.
        In case it's too big, we remove some words at the end.

        2) Retry loop (if we get an error after sending a query to GPT):
        On top of this there is a loop for retries (in case we get an error from GPT).
        On each retry we cut off the last document from the list. Documents in list are sorted by relevance,
        so each time we get rid of the least relevant document.

        Args:
            relevant_documents: List, documents identified as relevant to a question raised by a user.
            cut_off_cnt: Int, how many documents to remove from the end of the full list.
        """
        offset = 0.8  # Used as an estimated 'exchange rate' between a word and a token.
        document_context = "\n".join(
            map(
                lambda x: f"{x.content} {x.product.properties}",
                relevant_documents[: len(relevant_documents) - cut_off_cnt],
            )
        )
        tokens_cnt = len(self.ENCODING.encode(document_context))
        if tokens_cnt > self.MAX_TOKENS:
            words_to_remove = round(offset * (tokens_cnt - self.MAX_TOKENS))
            # Remove last words from the context to stay within a given limit.
            words = document_context.split()
            words = words[: len(words) - words_to_remove]
            document_context = " ".join(words)
        return document_context

    def run(self, full_user_request: str, keyword: str) -> str:
        product_retriever = self.injector.product_retriever
        relevant_documents = product_retriever.find_content_matching_query(full_user_request, keyword)
        retry = -1
        while retry < self.MAX_RETRY:
            try:
                retry += 1

                document_context = self._get_document_context(relevant_documents, retry)
                return document_context
            except Exception as error:
                logging.error(f"Problem with generating an answer. Retry: {retry}/{self.MAX_RETRY}. Error msg: {error}")

        error_msg = f"Unable to generate the answer. Total number of retries: {retry}"
        logging.error(error_msg)
        raise Exception(error_msg)

    def as_tool(self) -> StructuredTool:
        return StructuredTool.from_function(
            func=self.run,
            name=self.NAME,
            description=self.DESCRIPTION,
            args_schema=self.ARGS_SCHEMA,
            return_direct=self.RETURN_DIRECT,
        )
