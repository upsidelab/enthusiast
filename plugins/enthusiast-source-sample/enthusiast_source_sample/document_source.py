import csv
from pathlib import Path
from typing import Any

from enthusiast_common import DocumentDetails, DocumentSourcePlugin


class SampleDocumentSource(DocumentSourcePlugin):
    def __init__(self, data_set_id: Any):
        super().__init__(data_set_id)
        self.sample_file_path = Path(__file__).parent / "sample_documents.csv"

    def fetch(self) -> list[DocumentDetails]:
        results = []
        with open(self.sample_file_path, newline="", encoding="utf-8-sig") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                results.append(DocumentDetails(url=row["URL"], title=row["Title"], content=row["Content"]))

        return results
