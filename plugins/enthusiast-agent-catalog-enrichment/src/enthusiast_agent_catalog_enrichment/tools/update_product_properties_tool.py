import logging
from typing import Optional

from enthusiast_common.injectors import BaseInjector
from enthusiast_common.structures import ProductUpdateDetails
from enthusiast_common.tools import BaseLLMTool
from langchain_core.language_models import BaseLanguageModel
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class UpdateProductDetailsToolInput(BaseModel):
    product_sku: str = Field(description="string with product sku")
    name: Optional[str] = Field(description="string with product name")
    slug: Optional[str] = Field(description="string with product slug")
    description: Optional[str] = Field(description="string with product description")
    price: Optional[float] = Field(description="float with product price")
    property_values_by_property_name_as_json: Optional[str] = Field(description="""
    JSON string with product properties. It is to be decodable to a not nested, key-value dictionary,
    with property values by its name. It is to contain all product properties that were not matched 
    to the remaining defined properties""")


class UpdateProductPropertiesTool(BaseLLMTool):
    NAME = "update_product_properties"
    DESCRIPTION = "It's tool for updating product properties based on product sku and passed property names and values"
    ARGS_SCHEMA = UpdateProductDetailsToolInput
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
            property_values_by_property_name_as_json: Optional[str] = None
            ) -> Optional[str]:
        ecommerce_platform_connector = self.injector.ecommerce_platform_connector
        if not ecommerce_platform_connector:
            return "The user needs to configure an ecommerce platform connector first"

        try:
            product_details = ProductUpdateDetails(
                name=name,
                slug=slug,
                description=description,
                price=price,
                properties=property_values_by_property_name_as_json
            )
            product_exists = ecommerce_platform_connector.get_product_by_sku(product_sku) is not None

            if not product_exists:
                return "Failed to update product properties - the product with given sku does not exist"
            product_updated = ecommerce_platform_connector.update_product(product_sku, product_details)
            if product_updated:
                return "Product updated successfully"
            else:
                return "Failed to update product properties"
        except Exception as e:
            logger.error(e)
            return f"Error: {str(e)}"
