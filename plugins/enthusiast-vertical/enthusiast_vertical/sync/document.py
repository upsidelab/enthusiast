from enthusiast_vertical_common import DocumentSourcePlugin
from enthusiast_vertical_common.interfaces.integration_managers import BaseDocumentSourceManager

from enthusiast_vertical.models import Document


class DocumentSourceManager(BaseDocumentSourceManager):
    """Syncs documents from a DocumentSourcePlugin into the e-commerce domain definition."""

    def sync(self, plugin: DocumentSourcePlugin, dataset_id: int, integration_id: int) -> None:
        """Fetch documents via the plugin and upsert + index each one."""
        for details in plugin.fetch():
            document, _ = Document.objects.update_or_create(
                dataset_id=dataset_id,
                url=details.url,
                defaults={
                    "integration_id": integration_id,
                    "title": details.title,
                    "content": details.content,
                },
            )
            self._indexer.index(document)
