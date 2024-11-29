import logging

from celery import shared_task
from .models import DataSet

logger = logging.getLogger(__name__)

@shared_task()
def reload_all_embeddings_task(data_set_id):
    try:
        logging.debug("Start reloading all embeddings async task")
        logging.debug(f"- get data set with ID {data_set_id}")
        ds = DataSet.objects.get(id=data_set_id)
        logging.debug(f"- loaded data set with ID {data_set_id}")
        ds.reload_all_embeddings()
        logging.debug("Stop reloading all embeddings async task")
    except DataSet.DoesNotExist:
        # Handle the case where the order no longer exists
        logger.error("Data Set does not exist")
        raise


