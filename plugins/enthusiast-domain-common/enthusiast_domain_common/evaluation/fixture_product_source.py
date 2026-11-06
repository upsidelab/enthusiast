from ..interfaces import ProductSourcePlugin
from ..structures import ProductDetails


class FixtureProductSource(ProductSourcePlugin):
    """A product source serving a fixture catalog, so syncing fills a sandbox DataSet with it."""

    TYPE = "fixture_product_source"
    NAME = "Fixture products"

    def __init__(self, products: list[ProductDetails]):
        self._products = products

    def fetch(self) -> list[ProductDetails]:
        return list(self._products)
