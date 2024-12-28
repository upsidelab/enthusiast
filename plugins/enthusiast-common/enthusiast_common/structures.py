from dataclasses import dataclass


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

