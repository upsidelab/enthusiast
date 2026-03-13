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
    def on_chain_start(self, serialized, inputs, run_id, **kwargs):
        self.run_id = run_id
        self.send_message(
            {
                "type": "chat_message",
                "event": "start",
                "run_id": run_id,
            },
        )

    def on_llm_new_token(self, token: str, **kwargs):
        self.send_message(
            {
                "type": "chat_message",
                "event": "stream",
                "run_id": self.run_id,
                "token": token,
            },
        )

    def on_chain_end(self, outputs, **kwargs):
        self.send_message(
            {"type": "chat_message", "event": "end", "run_id": self.run_id, "output": outputs.get("output")},
        )
