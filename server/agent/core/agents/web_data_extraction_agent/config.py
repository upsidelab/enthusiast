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

from agent.callbacks import AgentActionWebsocketCallbackHandler, ReactAgentWebsocketCallbackHandler
from agent.conversation.service import ConversationService
from agent.core.agents.web_data_extraction_agent.agent import DataExtractionReActAgent
from agent.core.agents.web_data_extraction_agent.data_verification_tool import DataVerificationTool
from agent.core.agents.web_data_extraction_agent.prompt import DATA_EXTRACTION_AGENT_PROMPT
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


def get_config(conversation: Conversation, streaming: bool) -> AgentConfig:
    return AgentConfig(
        conversation_id=conversation.id,
        prompt_template=PromptTemplate(
            input_variables=["tools", "tool_names", "input", "agent_scratchpad", "output_format"],
            template=DATA_EXTRACTION_AGENT_PROMPT,
        ),
        agent_class=DataExtractionReActAgent,
        conversation_service=ConversationService,
        llm_tools=[
            LLMToolConfig(model_class=DataVerificationTool),
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
