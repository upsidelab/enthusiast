from functools import cached_property

from suvereo_common.evaluation.mocks import BaseMockIntegration, FixtureRecords

from ..interfaces import DocumentSourcePlugin
from ..structures import DocumentDetails
from .fixture_document import FixtureDocument


class DocumentMockIntegration(BaseMockIntegration, DocumentSourcePlugin):
    """Fixture documents for document agents, synced into a sandbox DataSet like a real document source."""

    TYPE = "mock_documents"
    NAME = "Mock document source"

    @classmethod
    def mock_classes(cls) -> tuple:
        return ()

    def fetch(self) -> list[DocumentDetails]:
        self._check_behaviour()
        return [document.to_document_details() for document in self._documents]

    @cached_property
    def _documents(self) -> list[FixtureDocument]:
        return FixtureDocument.load_all(FixtureRecords.load(self.config.data.get("documents"), self.base_dir))
