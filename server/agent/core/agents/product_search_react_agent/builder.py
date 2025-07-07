from enthusiast_common.retrievers import BaseVectorStoreRetriever
from enthusiast_common.services import BaseConversationService
from enthusiast_common.tools.base import BaseTool
from langchain_core.language_models import BaseLanguageModel
from langchain_core.prompts import ChatMessagePromptTemplate, PromptTemplate

from agent.core.agents.product_search_react_agent.agent import ProductSearchReActAgent
from agent.core.builder import AgentBuilder
from catalog.models import DocumentChunk, ProductContentChunk


class Builder(AgentBuilder):
    def _build_agent(
        self,
        tools: list[BaseTool],
        llm: BaseLanguageModel,
        prompt: PromptTemplate | ChatMessagePromptTemplate,
        conversation_service: BaseConversationService,
    ) -> ProductSearchReActAgent:
        return self._config.agent_class(
            tools=tools,
            llm=llm,
            prompt=prompt,
            conversation_service=conversation_service,
            conversation_id=self._config.conversation_id,
        )

    def _build_product_retriever(self) -> BaseVectorStoreRetriever[ProductContentChunk]:
        return self._config.retrievers.product.retriever_class.create(
            config=self._config,
            data_set_id=self._data_set_id,
            repositories=self._repositories,
            embeddings_registry=self._embeddings_registry,
            llm=self._llm,
        )

    def _build_document_retriever(self) -> BaseVectorStoreRetriever[DocumentChunk]:
        return self._config.retrievers.document.retriever_class.create(
            config=self._config,
            data_set_id=self._data_set_id,
            repositories=self._repositories,
            embeddings_registry=self._embeddings_registry,
            llm=self._llm,
        )
