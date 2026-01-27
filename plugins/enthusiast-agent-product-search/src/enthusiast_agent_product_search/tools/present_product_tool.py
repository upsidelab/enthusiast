import json

from django.forms import model_to_dict
from enthusiast_common.tools import BaseWidgetResponseLLMTool
from enthusiast_common.tools.interfaces import BaseWidgetResponseSerializer
from pydantic import BaseModel, Field


class PresentProductsToolSerializer(BaseWidgetResponseSerializer):
    def serialize(self):
        return model_to_dict(self.data)


class PresentProductsToolInput(BaseModel):
    products_ids: str = Field(description="Comma separated list of product ids")
    message_to_user: str = Field(description="Message to user that will go with products.")


class PresentProductsTool(BaseWidgetResponseLLMTool):
    NAME = "present_products_tool"
    DESCRIPTION = "IMPORTANT: *Always use this tool to show products to the user!*"
    ARGS_SCHEMA = PresentProductsToolInput
    RETURN_DIRECT = True
    SERIALIZER_CLASS = PresentProductsToolSerializer

    def run(self, products_ids: str, message_to_user: str):
        ids = products_ids.split(",")
        if self._streaming:
            self._injector.callbacks_handler.on_product_widget_start(
                json.dumps({"number_of_products": len(ids), "message": message_to_user})
            )
        all_products = []
        for id in ids:
            product = self._injector.repositories.product.get_by_id(int(id))
            serialized_product = self.SERIALIZER_CLASS(product).serialize()
            all_products.append(serialized_product)
            if self._streaming:
                self._injector.callbacks_handler.on_product_widget_product(serialized_product)
        if self._streaming:
            self._injector.callbacks_handler.on_product_widget_end()
        return json.dumps({"widget_type": "product_widget", "message": message_to_user, "data": all_products})
