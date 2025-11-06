import logging

from enthusiast_common.injectors import BaseInjector
from enthusiast_common.tools import BaseLLMTool
from enthusiast_common.utils import RequiredFieldsModel
from langchain_core.language_models import BaseLanguageModel
from pydantic import BaseModel, Field

from ..medusa_api_client import MedusaAPIClient

logger = logging.getLogger(__name__)


class OrderPlacementToolInput(BaseModel):
    product_ids: str = Field(description="comma separated string with products entry_ids")
    quantities: str = Field(description="comma separated string with products quantities")


class OrderPlacementToolConfiguration(RequiredFieldsModel):
    region_id: str = Field(
        title="Region ID",
        description="Medusa region id, will take first available region if not specified.",
        default="",
    )


class OrderPlacementTool(BaseLLMTool):
    NAME = "place_order_tool"
    DESCRIPTION = "It's tool for placing order and returning order URL based on products entry_ids"
    ARGS_SCHEMA = OrderPlacementToolInput
    CONFIGURATION_ARGS = OrderPlacementToolConfiguration
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
        try:
            quantities = quantities.split(",")
            medusa_client = MedusaAPIClient()
            region_id = self.CONFIGURATION_ARGS.region_id or medusa_client.list_regions()[0]["id"]
            variant_ids = [
                medusa_client.get_variants(product_id)["product"]["variants"][0]["id"]
                for product_id in product_ids.split(",")
            ]
            order_id = medusa_client.create_admin_order("user@example.com", variant_ids, quantities, region_id)[
                "draft_order"
            ]["id"]
            return f"Order placed successfully, url: http://localhost:9000/app/draft-orders/{order_id}"
        except Exception as e:
            logger.error(e)
            return f"Error: {str(e)}"
