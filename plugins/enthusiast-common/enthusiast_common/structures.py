from dataclasses import dataclass
from enum import Enum
from typing import Any

from pydantic import BaseModel

from .repositories import (
    BaseAgentRepository,
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
    properties: dict[str, Any]
    categories: list[str]
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
    agent: BaseAgentRepository


class FileTypes(Enum):
    FILE = "file"
    IMAGE = "image"


@dataclass
class LLMFile:
    id: Any
    content: str
    file_category: FileTypes
    filename: str
    content_type: str


class BaseContent(BaseModel):
    type: str


class TextContent(BaseContent):
    text: str


class BaseImageContent(BaseContent):
    pass


class BaseFileContent(BaseContent):
    pass
