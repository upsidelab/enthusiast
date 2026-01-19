import logging

from celery import shared_task

from catalog.models import DocumentSource, ECommerceIntegration, ProductSource
from sync.document.manager import DocumentSyncManager
from sync.ecommerce.manager import ECommerceSyncManager
from sync.product.manager import ProductSyncManager

logger = logging.getLogger(__name__)


@shared_task
def sync_product_source(source_id: int):
    product_source = ProductSource.objects.get(pk=source_id)
    if product_source.corrupted:
        logger.info(f"Product source: {product_source.plugin_name} {source_id} corrupted, skipping synchronization.")
        return
    manager = ProductSyncManager()
    manager.sync(source_id=source_id)


@shared_task
def sync_ecommerce_integration(integration_id: int):
    _integration = ECommerceIntegration.objects.get(pk=integration_id)
    manager = ECommerceSyncManager()
    manager.sync(source_id=integration_id)

@shared_task
def sync_data_set_product_sources(data_set_id: int):
    for source in ProductSource.objects.filter(data_set_id=data_set_id):
        sync_product_source.apply_async([source.id])


@shared_task
def sync_all_product_sources():
    for source in ProductSource.objects.all():
        sync_product_source.apply_async([source.id])

@shared_task
def sync_ecommerce_integrations(data_set_id: int):
    for integration in ECommerceIntegration.objects.filter(data_set_id=data_set_id):
        sync_ecommerce_integration.apply_async((integration.id,))

@shared_task
def sync_all_ecommerce_integrations():
    for integration in ECommerceIntegration.objects.all():
        sync_ecommerce_integration.apply_async((integration.id,))

@shared_task
def sync_document_source(source_id: int):
    document_source = DocumentSource.objects.get(pk=source_id)
    if document_source.corrupted:
        logger.info(f"Document source: {document_source.plugin_name} {source_id} corrupted, skipping synchronization.")
        return
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
    sync_all_ecommerce_integrations()
    sync_all_document_sources()
