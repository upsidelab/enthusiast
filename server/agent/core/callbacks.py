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


class ToolCallWebSocketCallbackHandler(BaseWebSocketHandler):
    def on_tool_start(self, serialized: dict, input_str: str, **kwargs) -> None:
        tool_name = serialized.get("name", "tool")
        self.send_message({"type": "chat_message", "event": "tool_call", "tool_name": tool_name, "display_input": None})

    def on_tool_end(self, output: Any, **kwargs) -> None:
        self.send_message({"type": "chat_message", "event": "tool_end"})

    def on_tool_error(self, error: BaseException, **kwargs) -> None:
        self.send_message({"type": "chat_message", "event": "tool_error"})
