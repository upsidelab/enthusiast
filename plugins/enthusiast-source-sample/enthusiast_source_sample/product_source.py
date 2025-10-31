import csv
from pathlib import Path
from typing import Any

from enthusiast_common import ProductDetails, ProductSourcePlugin


class SampleProductSource(ProductSourcePlugin):
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
                        properties={
                            "Internet Speed": row["Internet Speed"],
                            "Internet Package": row["Internet Package"],
                            "Landline Phone": row["Landline Phone"],
                            "Cable TV": row["Cable TV"],
                            "Router Included": row["Router Included"],
                            "Contract Length": row["Contract Length"],
                            "SLA": row["SLA"],
                        },
                        categories=[row["Categories"]],
                        price=row["Price"],
                    )
                )

        return results
