import logging
import json
from typing import Optional, List

from enthusiast_common import ProductDetails
from enthusiast_common.connectors import ECommercePlatformConnector
from enthusiast_common.injectors import BaseInjector
from enthusiast_common.structures import ProductUpdateDetails
from enthusiast_common.tools import BaseLLMTool
from langchain_core.language_models import BaseLanguageModel
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class UpsertProductDetailsInput(BaseModel):
    product_sku: str = Field(description="string with product sku")
    name: Optional[str] = Field(description="string with product name")
    slug: Optional[str] = Field(description="string with product slug")
    description: Optional[str] = Field(description="string with product description")
    price: Optional[str] = Field(description="string with product price as a decimal number")
    categories: Optional[str] = Field(description="comma separated string with product category names")
    property_values_by_property_name_as_json: Optional[str] = Field(description="""
    JSON string with product properties. It is to be decodable to a not nested, key-value dictionary,
    with property values by its name. It is to contain all product properties that were not matched 
    to the remaining defined properties. Values are to be strings, even for numeric of boolean properties.""")


class UpsertProductBatchInput(BaseModel):
    products: List[UpsertProductDetailsInput] = Field(
        description="List of products to upsert"
    )

class UpsertProductDetailsTool(BaseLLMTool):
    NAME = "upsert_product_properties"
    DESCRIPTION = "Tool for creating or updating products based on product SKUs and their properties."
    ARGS_SCHEMA = UpsertProductBatchInput
    RETURN_DIRECT = False

    def __init__(
            self,
            data_set_id: int,
            llm: BaseLanguageModel,
            injector: BaseInjector | None,
    ):
        super().__init__(data_set_id=data_set_id, llm=llm, injector=injector)
        self.data_set_id = data_set_id
        self.llm = llm
        self.injector = injector

    def run(self, products: List[UpsertProductDetailsInput]) -> str:
        ecommerce_platform_connector = self.injector.ecommerce_platform_connector

        if not ecommerce_platform_connector:
            return "The user needs to configure an ecommerce platform connector first"

        response = {}

        for product in products:
            product_sku = product.product_sku
            product_details = ProductUpdateDetails(
                name=product.name,
                slug=product.slug,
                description=product.description,
                price=float(product.price) if product.price else None,
                categories=product.categories,
                properties=product.property_values_by_property_name_as_json
            )
            product_upsert_result = None

            try:
                product_exists = ecommerce_platform_connector.get_product_by_sku(product_sku) is not None

                if product_exists:
                    product_upsert_result = self._update_product_details(ecommerce_platform_connector, product_sku, product_details)
                else:
                    product_upsert_result = self._create_product(ecommerce_platform_connector, product_sku, product_details)

            except Exception as e:
                logger.error(e)
                product_upsert_result =  f"Error: {str(e)}"

            response[product_sku] = product_upsert_result
        return json.dumps(response)

    @staticmethod
    def _update_product_details(connector: ECommercePlatformConnector,
                                product_sku: str,
                                product_details: ProductUpdateDetails) -> str:
        product_updated = connector.update_product(product_sku, product_details)
        if product_updated:
            return "Product updated successfully"
        else:
            return "Failed to update product properties"

    @staticmethod
    def _create_product(connector: ECommercePlatformConnector,
                        product_sku: str,
                        product_details: ProductUpdateDetails) -> str:

        product_create_details = ProductDetails(
            entry_id='',
            sku=product_sku,
            name=product_details.name,
            slug=product_details.slug,
            description=product_details.description,
            properties=product_details.properties,
            categories=product_details.categories,
            price=product_details.price,
        )

        connector.create_product(product_create_details)

        return "Product created successfully"
