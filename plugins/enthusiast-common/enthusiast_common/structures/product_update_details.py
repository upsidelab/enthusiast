from dataclasses import dataclass
from typing import Optional

@dataclass
class ProductUpdateDetails:
    name: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    sku: Optional[str] = None
    properties: Optional[str] = None
    categories: Optional[str] = None
    price: Optional[float] = None