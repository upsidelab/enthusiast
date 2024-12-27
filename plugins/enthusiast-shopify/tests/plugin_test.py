import unittest
from src.ecl_shopify_product_fetch.plugin import ShopifyProductFetch


class TestShopifyFetchPlugin(unittest.TestCase):
    def setUp(self):
        self.plugin = ShopifyProductFetch()

    def test_fetch(self):
        results = self.plugin.fetch()
        self.assertTrue(hasattr(results, '__iter__'), "fetch() should return an iterable")


if __name__ == "__main__":
    unittest.main()