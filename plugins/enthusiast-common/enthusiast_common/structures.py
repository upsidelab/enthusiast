from dataclasses import dataclass

from .repositories import (
    BaseConversationRepository,
    BaseDataSetRepository,
    BaseMessageRepository,
    BaseModelChunkRepository,
    BaseProductRepository,
    BaseUserRepository,
)


@dataclass
class ProductDetails:
    entry_id: str
    name: str
    slug: str
    description: str
    sku: str
    properties: str
    categories: str
    price: float


@dataclass
class DocumentDetails:
    url: str
    title: str
    content: str


@dataclass
class DocumentChunkDetails:
    content: str


@dataclass
class RepositoriesInstances:
    user: BaseUserRepository
    message: BaseMessageRepository
    conversation: BaseConversationRepository
    data_set: BaseDataSetRepository
    document_chunk: BaseModelChunkRepository
    product: BaseProductRepository
    product_chunk: BaseModelChunkRepository
