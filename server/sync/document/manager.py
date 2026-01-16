from enthusiast_common import DocumentDetails

from catalog.models import Document, DocumentSource
from catalog.tasks import index_document_task
from sync.base import DataSetSource, SyncManager
from sync.document.registry import DocumentSourcePluginRegistry


class DocumentSyncManager(SyncManager[DocumentDetails]):
    """Orchestrates synchronisation activities for document sync plugins."""

    def _build_registry(self):
        return DocumentSourcePluginRegistry()

    def _get_data_set_source(self, source_id: int) -> DataSetSource:
        source = DocumentSource.objects.get(id=source_id)
        return DataSetSource(plugin_name=source.plugin_name, data_set_id=source.data_set_id, config=source.config)

    def _sync_item(self, data_set_id: int, item_data: DocumentDetails):
        """Creates a document in the database.

        Args:
            data_set_id (int): obligatory, a data set to which imported data belongs to.
            item_data (dict): item details.
        """

        item, created = Document.objects.update_or_create(
            data_set_id=data_set_id,
            url=item_data.url,
            defaults={
                "title": item_data.title,
                "content": item_data.content,
            },
        )
        index_document_task.apply_async([item.id])
