from datetime import datetime, timedelta

from asgiref.sync import async_to_sync
from celery import Task, shared_task
from channels.layers import get_channel_layer
from django.utils import timezone

from agent.conversation import ConversationManager
from agent.core.callbacks import BaseWebSocketHandler
from agent.models import Message
from agent.models.conversation import ConversationFile
from pecl import settings


class SaveMessageOnFailureTask(Task):
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        conversation_id = kwargs.get("conversation_id")
        data_set_id = kwargs.get("data_set_id")
        user_id = kwargs.get("user_id")
        message = kwargs.get("message")

        Message.objects.create(
            conversation_id=conversation_id, created_at=datetime.now(), role="human", text=message, answer_failed=True
        )

        manager = ConversationManager()
        manager.record_error(conversation_id, user_id, data_set_id, exc)
        ws_handler = BaseWebSocketHandler(conversation_id=conversation_id)
        ws_handler.send_message({"type": "chat_message", "event": "error", "output": manager.DEFAULT_ERROR_MESSAGE})


@shared_task(base=SaveMessageOnFailureTask, bind=True, max_retries=3)
def respond_to_user_message_task(
    self, conversation_id: int, data_set_id: int, user_id: int, message: str, streaming: bool
):
    manager = ConversationManager()
    try:
        answer = manager.respond_to_user_message(
            conversation_id=conversation_id,
            data_set_id=data_set_id,
            user_id=user_id,
            message=message,
            streaming=streaming,
        )
        if streaming:
            channel_layer = get_channel_layer()
            group_name = f"conversation_{conversation_id}"
            async_to_sync(channel_layer.group_send)(
                group_name,
                {
                    "type": "chat_message",
                    "event": "message_created",
                    "answer_id": answer.id,
                },
            )
        return {"conversation_id": conversation_id, "message_id": answer.id}
    except Exception:
        self.retry(countdown=1)


@shared_task
def clean_uploaded_files():
    ConversationFile.objects.filter(
        created_at__lt=timezone.now() - timedelta(hours=settings.UPLOADED_FILE_RETENTION_PERIOD_HOURS)
    ).delete()
