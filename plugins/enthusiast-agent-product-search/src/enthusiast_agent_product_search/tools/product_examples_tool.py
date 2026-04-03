import textwrap

from enthusiast_common.tools import BaseLLMTool
from pydantic import BaseModel


class ProductExamplesToolSchema(BaseModel):
    pass


class ProductExamplesTool(BaseLLMTool):
    NAME = "product_examples"
    DESCRIPTION = "useful for understanding the product catalog"
    RETURN_DIRECT = False
    ARGS_SCHEMA = ProductExamplesToolSchema

    def format_display_output(self, output: str) -> str:
        try:
            start = output.index('[')
            end = output.rindex(']') + 1
            parsed = json.loads(output[start:end])
            if isinstance(parsed, list):
                n = len(parsed)
                return f"Retrieved {n} example product{'s' if n != 1 else ''}"
        except (ValueError, json.JSONDecodeError):
            pass
        return "Retrieved catalog examples"

    def run(self):
        product_retriever = self._injector.product_retriever
        sample_products = product_retriever.get_sample_products_json()
        response = f"""
            You can find a sample of products in the catalog below:
            {sample_products}
            Don't use any of these examples directly.
            Use the product search tool to find products matching user's query.
        """
        return textwrap.dedent(response)
