from catalog.models import DocumentSource, ProductSource
from celery import shared_task

from sync.document.manager import DocumentSyncManager
from sync.product.manager import ProductSyncManager


@shared_task
def sync_product_source(source_id: int):
    manager = ProductSyncManager()
    manager.sync(source_id=source_id)


@shared_task
def sync_data_set_product_sources(data_set_id: int):
    for source in ProductSource.objects.filter(data_set_id=data_set_id):
        sync_product_source.apply_async([source.id])


@shared_task
def sync_all_product_sources():
    for source in ProductSource.objects.all():
        sync_product_source.apply_async([source.id])


@shared_task
def sync_document_source(source_id: int):
    manager = DocumentSyncManager()
    manager.sync(source_id=source_id)


@shared_task
def sync_data_set_document_sources(data_set_id: int):
    for source in DocumentSource.objects.filter(data_set_id=data_set_id):
        sync_document_source.apply_async([source.id])


@shared_task
def sync_all_document_sources():
    for source in DocumentSource.objects.all():
        sync_document_source.apply_async([source.id])


@shared_task
def sync_data_set_all_sources(data_set_id: int):
    sync_data_set_product_sources(data_set_id)
    sync_data_set_document_sources(data_set_id)


@shared_task
def sync_all_sources():
    sync_all_product_sources()
    sync_all_document_sources()
