import logging

from enthusiast_common.injectors import BaseInjector
from enthusiast_common.tools import BaseLLMTool
from langchain_core.language_models import BaseLanguageModel
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class PlaceOrderToolInput(BaseModel):
    product_ids: str = Field(description="comma separated string with products entry_ids")
    quantities: str = Field(description="comma separated string with products quantities")


class PlaceOrderTool(BaseLLMTool):
    NAME = "place_order"
    DESCRIPTION = "It's tool for placing order and returning order URL based on products entry_ids"
    ARGS_SCHEMA = PlaceOrderToolInput
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

    def run(self, product_ids: str, quantities: str) -> str | None:
        ecommerce_platform_connector = self.injector.ecommerce_platform_connector
        if not ecommerce_platform_connector:
            return "The user needs to configure an ecommerce platform connector first"

        try:
            product_ids_list = product_ids.split(",")
            quantities_list = quantities.split(",")
            order_id = ecommerce_platform_connector.create_order_with_items(list(zip(product_ids_list, quantities_list)))
            return f"Order placed successfully, url: http://localhost:9000/app/draft-orders/{order_id}"
        except Exception as e:
            logger.error(e)
            return f"Error: {str(e)}"
