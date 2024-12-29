from enthusiast_common import DocumentDetails

from catalog.models import Document, DocumentSource
from catalog.tasks import index_document_task
from sync.base import DataSetSource, SyncManager
from sync.document.registry import DocumentSourcePluginRegistry


class DocumentSyncManager(SyncManager[DocumentDetails]):
    """Orchestrates synchronisation activities for document sync plugins."""

    def _build_registry(self):
        return DocumentSourcePluginRegistry()

    def _get_all_sources(self) -> list[DataSetSource]:
        all_sources = [DataSetSource(plugin_name=source.plugin_name, 
                                     data_set_id=source.data_set_id,
                                     config=source.config)
                       for source in DocumentSource.objects.all()]
        return all_sources

    def _get_data_set_sources(self, data_set_id: int) -> list[DataSetSource]:
        data_set_sources = [DataSetSource(plugin_name=source.plugin_name, 
                                          data_set_id=source.data_set_id,
                                          config=source.config)
                            for source in DocumentSource.objects.filter(data_set_id=data_set_id)]
        return data_set_sources

    def _get_data_set_source(self, source_id: int) -> DataSetSource:
        source = DocumentSource.objects.get(id=source_id)
        return DataSetSource(plugin_name=source.plugin_name, 
                             data_set_id=source.data_set_id,
                             config=source.config)

    def _sync_item(self, data_set_id: int, item_data: DocumentDetails):
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
        index_document_task.apply_async([item.id])
