from catalog.models import ProductSource
from celery import shared_task

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
