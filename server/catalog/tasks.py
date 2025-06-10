import logging

from celery import shared_task

from .models import DataSet, Document, Product
from .services import DocumentEmbeddingGenerator, ProductEmbeddingGenerator

logger = logging.getLogger(__name__)


@shared_task
def index_document_task(document_id: int):
    document = Document.objects.get(id=document_id)
    DocumentEmbeddingGenerator.index_object(document)


@shared_task
def index_all_documents_task(data_set_id: int):
    data_set = DataSet.objects.get(id=data_set_id)
    document_ids = data_set.documents.values_list("id", flat=True)
    for document_id in document_ids:
        index_document_task.apply_async([document_id])


@shared_task
def index_product_task(product_id: int):
    product = Product.objects.get(id=product_id)
    ProductEmbeddingGenerator.index_object(product)
