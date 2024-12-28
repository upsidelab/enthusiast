import csv
from pathlib import Path

from enthusiast_common import ProductSourcePlugin, ProductDetails


class SampleProductSource(ProductSourcePlugin):
    def __init__(self, data_set_id: int, config: dict):
        super().__init__(data_set_id, config)
        self.sample_file_path = Path(__file__).parent / "sample_products.csv"

    def fetch(self) -> list[ProductDetails]:
        results = []
        with open(self.sample_file_path, newline='', encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                results.append(ProductDetails(
                    entry_id=row['ID'],
                    name=row['Name'],
                    slug=row['SKU'],
                    sku=row['SKU'],
                    description=row['Description'],
                    properties=row['Merged Properties'],
                    categories=row['Categories'],
                    price=row['Price']
                ))

        return results
