import logging

from enthusiast_common.injectors import BaseInjector
from enthusiast_common.tools import BaseLLMTool
from enthusiast_common.utils import RequiredFieldsModel
from langchain_core.language_models import BaseLanguageModel
from pydantic import BaseModel, Field

from ..medusa_api_client import MedusaAPIClient

logger = logging.getLogger(__name__)


class PlaceOrderToolInput(BaseModel):
    product_ids: str = Field(description="comma separated string with products entry_ids")
    quantities: str = Field(description="comma separated string with products quantities")


class PlaceOrderToolConfirmation(RequiredFieldsModel):
    region_id: str = Field(
        title="Region ID",
        description="Medusa region id, will take first available region if not specified.",
        default="",
    )
    medusa_api_key: str = Field(
        title="Medusa API key",
        description="Medusa API key, to authenticate to API.",
    )
    medusa_base_url: str = Field(
        title="Medusa base url",
        description="Medusa API base url.",
    )


class PlaceOrderTool(BaseLLMTool):
    NAME = "place_order"
    DESCRIPTION = "It's tool for placing order and returning order URL based on products entry_ids"
    ARGS_SCHEMA = PlaceOrderToolInput
    CONFIGURATION_ARGS = PlaceOrderToolConfirmation
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
            medusa_client = MedusaAPIClient(
                api_key=self.CONFIGURATION_ARGS.medusa_api_key, base_url=self.CONFIGURATION_ARGS.medusa_base_url
            )
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
