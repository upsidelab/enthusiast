from catalog.models import Document
from sync.base import SyncManager
from common.plugin.interface import ItemData
from sync.document.registry import DocumentSourcePluginRegistry


class DocumentSyncManager(SyncManager):
    """Orchestrates synchronisation activities for document sync plugins."""

    def _build_registry(self):
        return DocumentSourcePluginRegistry()

    def _sync_item(self, data_set_id: int, item_data: ItemData):
        """Creates a document in the database.

        Args:
            data_set_id (int): obligatory, a data set to which imported data belongs to.
            item_data (dict): item details.
        """

        item, created = Document.objects.update_or_create(
            url=item_data.url,
            defaults={
                "data_set_id": data_set_id,
                "title": item_data.title,
                "content": item_data.content,
            }
        )

