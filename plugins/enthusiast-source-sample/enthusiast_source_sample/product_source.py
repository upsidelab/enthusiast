import csv
from pathlib import Path
from typing import Any

from enthusiast_common import ProductDetails, ProductSourcePlugin


class SampleProductSource(ProductSourcePlugin):
    NAME = "Sample Product Source"

    def __init__(self, data_set_id: Any):
        super().__init__(data_set_id)
        self.sample_file_path = Path(__file__).parent / "sample_products.csv"

    def fetch(self) -> list[ProductDetails]:
        results = []
        with open(self.sample_file_path, newline="", encoding="utf-8-sig") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                results.append(
                    ProductDetails(
                        entry_id=row["ID"],
                        name=row["Name"],
                        slug=row["SKU"],
                        sku=row["SKU"],
                        description=row["Description"],
                        properties=row["Merged Properties"],
                        categories=row["Categories"],
                        price=row["Price"],
                    )
                )

        return results
