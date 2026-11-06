import re
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator
from suvereo_common.evaluation.mocks import MockConfigError

from ..structures import ProductDetails


class CatalogProduct(BaseModel):
    """A product in a fixture catalog; only sku and name are required, blank or missing values take defaults."""

    model_config = ConfigDict(extra="ignore", coerce_numbers_to_str=True)

    sku: str
    name: str
    entry_id: str = ""
    slug: str = ""
    description: str = ""
    properties: str = ""
    categories: str = ""
    price: float = 0.0
    stock: int = Field(default=0, description="Starting stock for update_stock; not part of ProductDetails.")

    @model_validator(mode="before")
    @classmethod
    def _blank_cells_are_unset(cls, data: Any) -> Any:
        if isinstance(data, dict):
            return {k: v for k, v in data.items() if v is not None and not (isinstance(v, str) and not v.strip())}
        return data

    @classmethod
    def load_all(cls, records: list[dict[str, Any]]) -> list["CatalogProduct"]:
        """Validate a catalog's records; raises MockConfigError naming the first invalid one."""
        try:
            return [cls.model_validate(record) for record in records]
        except ValidationError as e:
            raise MockConfigError(f"Invalid catalog product: {e}") from e

    def to_product_details(self) -> ProductDetails:
        """The product as the platform connector and product source return it."""
        return ProductDetails(
            entry_id=self.entry_id or self.sku,
            name=self.name,
            slug=self.slug or re.sub(r"[^a-z0-9]+", "-", self.name.lower()).strip("-"),
            description=self.description,
            sku=self.sku,
            properties=self.properties,
            categories=self.categories,
            price=self.price,
        )
