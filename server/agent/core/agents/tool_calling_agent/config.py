from enthusiast_common.config import (
    EmbeddingsRegistryConfig,
    LLMConfig,
    LLMRegistryConfig,
    LLMToolConfig,
    ModelsRegistryConfig,
    RegistryConfig,
    RepositoriesConfig,
    RetrieverConfig,
    RetrieversConfig,
    ToolCallingAgentConfig,
)
from langchain_core.prompts import ChatPromptTemplate

from agent.callbacks import ConversationWebSocketCallbackHandler
from agent.core.agents import ToolCallingAgent
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
        llm_tools=[
            LLMToolConfig(
                tool_class=CreateAnswerTool,
            )
        ],
        llm=LLMConfig(callbacks=[ConversationWebSocketCallbackHandler(conversation.id)], streaming=streaming),
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
            product=RetrieverConfig(
                retriever_class=ProductRetriever,
                extra_kwargs={
                    "prompt_template": QUERY_PROMPT_TEMPLATE,
                    "max_sample_products": 12,
                    "number_of_products": 12,
                },
            ),
        ),
        registry=RegistryConfig(
            llm=LLMRegistryConfig(registry_class=LanguageModelRegistry),
            embeddings=EmbeddingsRegistryConfig(registry_class=EmbeddingProviderRegistry),
            model=ModelsRegistryConfig(registry_class=BaseDjangoSettingsDBModelRegistry),
        ),
    )
