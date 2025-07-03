from enthusiast_common.config import (
    AgentCallbackHandlerConfig,
    AgentConfig,
    EmbeddingsRegistryConfig,
    LLMConfig,
    LLMRegistryConfig,
    LLMToolConfig,
    ModelsRegistryConfig,
    RegistryConfig,
    RepositoriesConfig,
    RetrieverConfig,
    RetrieversConfig,
)
from langchain_core.callbacks import StdOutCallbackHandler
from langchain_core.prompts import PromptTemplate

from agent.callbacks import AgentActionWebsocketCallbackHandler
from agent.callbacks import ReactAgentWebsocketCallbackHandler
from agent.core.agents.product_search_react_agent.agent import ProductSearchReActAgent
from agent.core.agents.product_search_react_agent.prompt import PRODUCT_FINDER_AGENT_PROMPT
from agent.injector import Injector
from agent.models import Conversation
from agent.registries.embeddings import EmbeddingProviderRegistry
from agent.registries.language_models import LanguageModelRegistry
from agent.registries.models import BaseDjangoSettingsDBModelRegistry
from agent.repositories import (
    DjangoConversationRepository,
    DjangoDataSetRepository,
    DjangoDocumentChunkRepository,
    DjangoMessageRepository,
    DjangoProductChunkRepository,
    DjangoProductRepository,
    DjangoUserRepository,
)
from agent.retrievers import DocumentRetriever
from agent.retrievers.product_vs_retriever import ProductVectorStoreRetriever
from agent.tools import ProductVectorStoreSearchTool
from agent.tools.verify_product_tool import ProductVerificationTool


def get_config(conversation: Conversation, streaming: bool) -> AgentConfig:
    return AgentConfig(
        conversation_id=conversation.id,
        prompt_template=PromptTemplate(
            input_variables=["tools", "tool_names", "input", "agent_scratchpad"], template=PRODUCT_FINDER_AGENT_PROMPT
        ),
        agent_class=ProductSearchReActAgent,
        llm_tools=[
            LLMToolConfig(
                tool_class=ProductVectorStoreSearchTool,
            ),
            LLMToolConfig(tool_class=ProductVerificationTool),
        ],
        llm=LLMConfig(
            callbacks=[ReactAgentWebsocketCallbackHandler(conversation.id), StdOutCallbackHandler()],
            streaming=streaming,
        ),
        injector=Injector,
        repositories=RepositoriesConfig(
            user=DjangoUserRepository,
            data_set=DjangoDataSetRepository,
            conversation=DjangoConversationRepository,
            message=DjangoMessageRepository,
            product=DjangoProductRepository,
            document_chunk=DjangoDocumentChunkRepository,
            product_chunk=DjangoProductChunkRepository,
        ),
        retrievers=RetrieversConfig(
            document=RetrieverConfig(retriever_class=DocumentRetriever),
            product=RetrieverConfig(retriever_class=ProductVectorStoreRetriever, extra_kwargs={"max_objects": 30}),
        ),
        registry=RegistryConfig(
            llm=LLMRegistryConfig(registry_class=LanguageModelRegistry),
            embeddings=EmbeddingsRegistryConfig(registry_class=EmbeddingProviderRegistry),
            model=ModelsRegistryConfig(registry_class=BaseDjangoSettingsDBModelRegistry),
        ),
        agent_callback_handler=AgentCallbackHandlerConfig(
            handler_class=AgentActionWebsocketCallbackHandler, args={"conversation_id": conversation.id}
        ),
    )
