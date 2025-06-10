import logging

from celery import shared_task
from .models import DataSet, Document
from .services import index_document

logger = logging.getLogger(__name__)


@shared_task
def index_document_task(document_id: int):
    document = Document.objects.get(id=document_id)
    index_document(document)


@shared_task
def index_all_documents_task(data_set_id: int):
    data_set = DataSet.objects.get(id=data_set_id)
    document_ids = data_set.documents.values_list("id", flat=True)
    for document_id in document_ids:
        index_document_task.apply_async([document_id])
