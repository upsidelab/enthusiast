from typing import Any

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from enthusiast_common.callbacks import ConversationCallbackHandler


class BaseWebSocketHandler(ConversationCallbackHandler):
    def __init__(self, conversation_id: int):
        self.group_name = f"conversation_{conversation_id}"
        self.channel_layer = get_channel_layer()
        self.run_id = None

    def send_message(self, message_data: Any) -> None:
        async_to_sync(self.channel_layer.group_send)(self.group_name, message_data)


class ConversationWebSocketCallbackHandler(BaseWebSocketHandler):
    def on_llm_new_token(self, token: str, **kwargs):
        if not token:
            return
        self.send_message({"type": "chat_message", "event": "stream", "token": token})
