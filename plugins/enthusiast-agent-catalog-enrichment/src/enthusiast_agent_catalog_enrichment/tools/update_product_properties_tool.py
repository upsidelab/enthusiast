import logging
from typing import Optional

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
    price: Optional[float] = Field(description="float with product price")
    categories: Optional[str] = Field(description="comma separated string with product category names")
    property_values_by_property_name_as_json: Optional[str] = Field(description="""
    JSON string with product properties. It is to be decodable to a not nested, key-value dictionary,
    with property values by its name. It is to contain all product properties that were not matched 
    to the remaining defined properties""")


class UpsertProductDetailsTool(BaseLLMTool):
    NAME = "upsert_product_properties"
    DESCRIPTION = "It's tool for creating/updating product properties based on product sku and passed property names and values"
    ARGS_SCHEMA = UpsertProductDetailsInput
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

    def run(self,
            product_sku: str,
            name: Optional[str] = None,
            slug: Optional[str] = None,
            description: Optional[str] = None,
            price: Optional[float] = None,
            categories: Optional[str] = None,
            property_values_by_property_name_as_json: Optional[str] = None
            ) -> Optional[str]:
        ecommerce_platform_connector = self.injector.ecommerce_platform_connector

        if not ecommerce_platform_connector:
            return "The user needs to configure an ecommerce platform connector first"

        product_details = ProductUpdateDetails(
            name=name,
            slug=slug,
            description=description,
            price=price,
            categories=categories,
            properties=property_values_by_property_name_as_json
        )

        try:
            product_exists = ecommerce_platform_connector.get_product_by_sku(product_sku) is not None

            if product_exists:
                self._update_product_details(ecommerce_platform_connector, product_sku, product_details)
            else:
                self._create_product(ecommerce_platform_connector, product_sku, product_details)

        except Exception as e:
            logger.error(e)
            return f"Error: {str(e)}"

    @staticmethod
    def _update_product_details(connector: ECommercePlatformConnector,
                                product_sku: str,
                                product_details: ProductUpdateDetails) -> str:
        product_updated = connector.update_product(product_sku, product_details)
        if product_updated:
            return "Product updated successfully"
        else:
            return "Failed to update product properties"

    def _create_product(self,
                        connector: ECommercePlatformConnector,
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

        self._raise_missing_create_details(product_create_details)

        connector.create_product(product_create_details)

        return "Product created successfully"

    @staticmethod
    def _raise_missing_create_details(product_details: ProductDetails) -> None:
        property_by_name = {
            "sku": product_details.sku,
            "name": product_details.name,
            "slug": product_details.slug,
            "description": product_details.description,
            "properties": product_details.properties,
            "categories": product_details.categories,
            "price": product_details.price,
        }

        missing_properties = []

        for key, value in property_by_name.items():
            if value is None:
                missing_properties.append(key)

        if len(missing_properties) == 0:
            return

        raise Exception("Could not create product because of missing properties: " + str(missing_properties))
