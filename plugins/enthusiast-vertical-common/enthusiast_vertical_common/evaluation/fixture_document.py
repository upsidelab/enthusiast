from typing import Any

from pydantic import BaseModel, ConfigDict, ValidationError
from suvereo_common.evaluation.mocks import MockConfigError

from ..structures import DocumentDetails


class FixtureDocument(BaseModel):
    """A document in a fixture set, synced like one fetched from a real document source."""

    model_config = ConfigDict(extra="ignore")

    url: str
    title: str
    content: str

    @classmethod
    def load_all(cls, records: list[dict[str, Any]]) -> list["FixtureDocument"]:
        """Validate a fixture set's records; raises MockConfigError naming the first invalid one."""
        try:
            return [cls.model_validate(record) for record in records]
        except ValidationError as e:
            raise MockConfigError(f"Invalid fixture document: {e}") from e

    def to_document_details(self) -> DocumentDetails:
        """The document as the document source returns it."""
        return DocumentDetails(url=self.url, title=self.title, content=self.content)
