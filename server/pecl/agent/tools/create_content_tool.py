import logging
import tiktoken

from typing import Type, Any

from django.core import serializers
from langchain_core.prompts import PromptTemplate
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

from agent.core import LlmProvider
from agent.retrievers import DocumentRetriever
from agent.retrievers import ProductRetriever
from ecl.models import DataSet, EmbeddingModel, EmbeddingDimension

logger = logging.getLogger(__name__)

CREATE_CONTENT_PROMPT_TEMPLATE = """
    Based on the following documents delimited by three backticks
    ```
    {document_context}
    ```
    and the following products delimited by three backticks
    ```
    {product_context}
    ```
    create content for the following user request delimited by three backticks
    ```
    {query}
    ``` 
"""


class CreateContentToolInput(BaseModel):
    query: str = Field(description="user's request")


class CreateContentTool(BaseTool):
    name: str = "create_content_tool"
    description: str = "use it when asked to generate content about products"
    args_schema: Type[BaseModel] = CreateContentToolInput
    return_direct: bool = True
    data_set: DataSet = None
    embedding_model: EmbeddingModel = None
    embedding_dimensions: EmbeddingDimension = None
    encoding: tiktoken.encoding_for_model = None
    max_tokens: int = 30000
    max_retry: int = 3
    chat_model: str = None

    def __init__(self, data_set: DataSet, embedding_model: EmbeddingModel,
                 embedding_dimensions: EmbeddingDimension, chat_model: str, **kwargs: Any):
        super().__init__(**kwargs)
        self.data_set = data_set
        self.embedding_model = embedding_model
        self.embedding_dimensions = embedding_dimensions
        self.chat_model = chat_model
        self.encoding = tiktoken.encoding_for_model(chat_model)

    def _get_document_context(self, relevant_documents, cut_off_cnt):
        """ Identify document context for a query.

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
        document_context = ' '.join(map(lambda x: x.content, relevant_documents[:len(relevant_documents) - cut_off_cnt]))
        tokens_cnt = len(self.encoding.encode(document_context))
        if tokens_cnt > self.max_tokens:
            words_to_remove = round(offset * (tokens_cnt - self.max_tokens))
            # Remove last words from the context to stay within a given limit.
            words = document_context.split()
            words = words[:len(words) - words_to_remove]
            document_context = ' '.join(words)
        return document_context

    def _run(self, query: str):
        document_retriever = DocumentRetriever(data_set=self.data_set, embedding_model=self.embedding_model,
                                               embedding_dimensions=self.embedding_dimensions)
        relevant_documents = document_retriever.find_documents_matching_query(query)
        relevant_products = ProductRetriever(data_set=self.data_set).find_products_matching_query(query)

        product_context = serializers.serialize("json", relevant_products)

        chain = PromptTemplate.from_template(CREATE_CONTENT_PROMPT_TEMPLATE) | LlmProvider.provide_llm_instance()

        retry = -1
        while retry < self.max_retry:
            try:
                retry += 1

                document_context = self._get_document_context(relevant_documents, retry)

                llm_result = chain.invoke({
                    "query": query,
                    "document_context": document_context,
                    "product_context": product_context
                })
                return llm_result.content
            except Exception as error:
                logging.debug(f"Problem with generating an answer. Retry: {retry}/{self.max_retry}. Error msg: {error}")

        error_msg = f"Unable to generate the answer. Total number of retries: {retry}"
        logging.error(error_msg)
        raise Exception(error_msg)