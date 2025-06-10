from enthusiast_common.config import (
    ToolCallingAgentConfig,
    LLMToolConfig,
    LLMConfig,
    RepositoriesConfig,
    RetrieversConfig,
    RegistryConfig,
    LLMRegistryConfig,
    EmbeddingsRegistryConfig,
    ModelsRegistryConfig,
    DocumentRetrieverConfig,
    ProductRetrieverConfig,
)
from langchain_core.prompts import ChatPromptTemplate

from agent.callbacks import ConversationWebSocketCallbackHandler
from agent.conversation.service import ConversationService
from agent.core.agents import ToolCallingAgent
from agent.injector import Injector
from agent.models import Conversation
from agent.registries.embeddings import EmbeddingProviderRegistry
from agent.registries.language_models import LanguageModelRegistry
from agent.registries.models import BaseDjangoSettingsDBModelRegistry
from agent.repositories import (
    DjangoUserRepository,
    DjangoDataSetRepository,
    DjangoConversationRepository,
    DjangoMessageRepository,
    DjangoProductRepository,
    DjangoDocumentChunkRepository,
)
from agent.retrievers import DocumentRetriever, ProductRetriever
from agent.retrievers.product_retriever import QUERY_PROMPT_TEMPLATE
from agent.tools import CreateAnswerTool


def get_config(conversation: Conversation, streaming: bool) -> ToolCallingAgentConfig:
    return ToolCallingAgentConfig(
        conversation_id=conversation.id,
        prompt_template=ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a sales support agent, and you know everything about a company and their products.",
                ),
                ("placeholder", "{chat_history}"),
                ("human", "{input}"),
                ("placeholder", "{agent_scratchpad}"),
            ]
        ),
        agent_class=ToolCallingAgent,
        conversation_service=ConversationService,
        llm_tools=[
            LLMToolConfig(
                model_class=CreateAnswerTool,
            )
        ],
        llm=LLMConfig(callbacks=[ConversationWebSocketCallbackHandler(conversation)], streaming=streaming),
        injector=Injector,
        repositories=RepositoriesConfig(
            user=DjangoUserRepository,
            data_set=DjangoDataSetRepository,
            conversation=DjangoConversationRepository,
            message=DjangoMessageRepository,
            product=DjangoProductRepository,
            document_chunk=DjangoDocumentChunkRepository,
        ),
        retrievers=RetrieversConfig(
            document=DocumentRetrieverConfig(retriever_class=DocumentRetriever),
            product=ProductRetrieverConfig(retriever_class=ProductRetriever, prompt_template=QUERY_PROMPT_TEMPLATE),
        ),
        registry=RegistryConfig(
            llm=LLMRegistryConfig(registry_class=LanguageModelRegistry),
            embeddings=EmbeddingsRegistryConfig(registry_class=EmbeddingProviderRegistry),
            model=ModelsRegistryConfig(registry_class=BaseDjangoSettingsDBModelRegistry),
        ),
    )
