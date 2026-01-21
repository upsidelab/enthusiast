from dataclasses import dataclass

from enthusiast_common.repositories import (
    BaseAgentRepository,
    BaseConversationRepository,
    BaseDataSetRepository,
    BaseMessageRepository,
    BaseModelChunkRepository,
    BaseProductRepository,
    BaseUserRepository,
)


@dataclass
class RepositoriesInstances:
    user: BaseUserRepository
    message: BaseMessageRepository
    conversation: BaseConversationRepository
    data_set: BaseDataSetRepository
    document_chunk: BaseModelChunkRepository
    product: BaseProductRepository
    product_chunk: BaseModelChunkRepository
    agent: BaseAgentRepository
