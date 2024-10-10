from typing import Type, Any

from django.core import serializers
from langchain_core.prompts import PromptTemplate
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

from agent.core import LlmProvider
from agent.retrievers import DocumentRetriever
from agent.retrievers import ProductRetriever
from ecl.models import DataSet

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

    def __init__(self, data_set: DataSet, **kwargs: Any):
        super().__init__(**kwargs)
        self.data_set = data_set

    def _run(self, query: str):
        relevant_documents = DocumentRetriever(data_set=self.data_set).find_documents_matching_query(query)
        relevant_products = ProductRetriever(data_set=self.data_set).find_products_matching_query(query)

        document_context = ' '.join(map(lambda x: x.content, relevant_documents))
        product_context = serializers.serialize("json", relevant_products)

        chain = PromptTemplate.from_template(CREATE_CONTENT_PROMPT_TEMPLATE) | LlmProvider.provide_llm_instance()
        llm_result = chain.invoke({
            "query": query,
            "document_context": document_context,
            "product_context": product_context
        })
        return llm_result.content
