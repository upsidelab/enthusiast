import logging
import tiktoken

from typing import Type, Any, Optional

from django.core import serializers
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field

from agent.retrievers import DocumentRetriever
from agent.retrievers import ProductRetriever
from catalog.models import DataSet

from enthusiast_common.interfaces import CustomTool, LanguageModelProvider

logger = logging.getLogger(__name__)

CREATE_CONTENT_PROMPT_TEMPLATE = """
    You're supporting a sales agent or a customer support representative, in answering questions they get from the customers.
    
    Based on the following documents delimited by three backticks
    ```
    {document_context}
    ```
    and the following products delimited by three backticks
    ```
    {product_context}
    ```
    respond to the following user request delimited by three backticks
    ```
    {query}
    ``` 
    Be concise and make sure that the response is to the point. Don't include unnecessary information.
"""


class CreateAnswerToolInput(BaseModel):
    full_user_request: str = Field(description="user's full request")


class CreateAnswerTool(CustomTool):
    name: str = "create_answer_tool"
    description: str = "use it when asked to generate content or answer a question about products"
    args_schema: Type[BaseModel] = CreateAnswerToolInput
    return_direct: bool = True
    data_set: any = None
    chat_model: Optional[str] = None
    encoding: tiktoken.encoding_for_model = None
    max_tokens: int = 30000
    max_retry: int = 3

    def __init__(self,
                 data_set: DataSet,
                 chat_model: str,
                 language_model_provider: LanguageModelProvider,
                 **kwargs: Any):
        super().__init__(data_set=data_set, chat_model=chat_model, language_model_provider=language_model_provider,
                         **kwargs)
        if language_model_provider.model_name() in tiktoken.model.MODEL_TO_ENCODING:
            self.encoding = tiktoken.encoding_for_model(language_model_provider.model_name())
        else:
            self.encoding = tiktoken.encoding_for_model("gpt-4o")

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

    def _run(self, full_user_request: str):
        document_retriever = DocumentRetriever(data_set=self.data_set)
        relevant_documents = document_retriever.find_documents_matching_query(full_user_request)
        relevant_products = ProductRetriever(data_set=self.data_set).find_products_matching_query(full_user_request)

        product_context = serializers.serialize("json", relevant_products)

        prompt = PromptTemplate.from_template(CREATE_CONTENT_PROMPT_TEMPLATE)
        llm = self._language_model_provider.provide_language_model()
        chain = prompt | llm

        retry = -1
        while retry < self.max_retry:
            try:
                retry += 1

                document_context = self._get_document_context(relevant_documents, retry)

                llm_result = chain.invoke({
                    "query": full_user_request,
                    "document_context": document_context,
                    "product_context": product_context
                })
                return llm_result.content
            except Exception as error:
                logging.error(f"Problem with generating an answer. Retry: {retry}/{self.max_retry}. Error msg: {error}")

        error_msg = f"Unable to generate the answer. Total number of retries: {retry}"
        logging.error(error_msg)
        raise Exception(error_msg)
