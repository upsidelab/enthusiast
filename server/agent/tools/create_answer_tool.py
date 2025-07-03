import logging

import tiktoken
from django.core import serializers
from enthusiast_common.injectors import BaseInjector
from enthusiast_common.tools import BaseLLMTool
from langchain_core.language_models import BaseLanguageModel
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field

from agent.repositories import DjangoDataSetRepository

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


class CreateAnswerTool(BaseLLMTool):
    NAME = "create_answer_tool"
    DESCRIPTION = "use it when asked to generate content or answer a question about products"
    ARGS_SCHEMA = CreateAnswerToolInput
    RETURN_DIRECT = True

    ENCODING: tiktoken.encoding_for_model = None
    MAX_TOKENS: int = 30000
    MAX_RETRY: int = 3

    def __init__(
        self,
        data_set_id: int,
        data_set_repo: DjangoDataSetRepository,
        llm: BaseLanguageModel,
        injector: BaseInjector,
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
        document_context = " ".join(
            map(lambda x: x.content, relevant_documents[: len(relevant_documents) - cut_off_cnt])
        )
        tokens_cnt = len(self.ENCODING.encode(document_context))
        if tokens_cnt > self.MAX_TOKENS:
            words_to_remove = round(offset * (tokens_cnt - self.MAX_TOKENS))
            # Remove last words from the context to stay within a given limit.
            words = document_context.split()
            words = words[: len(words) - words_to_remove]
            document_context = " ".join(words)
        return document_context

    def run(self, full_user_request: str):
        document_retriever = self.injector.document_retriever
        product_retriever = self.injector.product_retriever
        relevant_documents = document_retriever.find_content_matching_query(full_user_request)
        relevant_products = product_retriever.find_products_matching_query(full_user_request)

        product_context = serializers.serialize("json", relevant_products)

        prompt = PromptTemplate.from_template(CREATE_CONTENT_PROMPT_TEMPLATE)
        chain = prompt | self.llm

        retry = -1
        while retry < self.MAX_RETRY:
            try:
                retry += 1

                document_context = self._get_document_context(relevant_documents, retry)

                llm_result = chain.invoke(
                    {
                        "query": full_user_request,
                        "document_context": document_context,
                        "product_context": product_context,
                    }
                )
                return llm_result.content
            except Exception as error:
                logging.error(f"Problem with generating an answer. Retry: {retry}/{self.MAX_RETRY}. Error msg: {error}")

        error_msg = f"Unable to generate the answer. Total number of retries: {retry}"
        logging.error(error_msg)
        raise Exception(error_msg)
