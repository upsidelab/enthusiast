from asgiref.sync import async_to_sync
from celery import shared_task
from channels.layers import get_channel_layer

from agent.conversation import ConversationManager


@shared_task(bind=True, max_retries=3)
def respond_to_user_message_task(
    self, conversation_id: int, data_set_id: int, user_id: int, message: str, streaming: bool
):
    manager = ConversationManager()
    try:
        answer = manager.respond_to_user_message(conversation_id, data_set_id, user_id, message, streaming)
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
    except Exception as e:
        manager.record_error(conversation_id, user_id, data_set_id, e)
        self.retry(countdown=1)
