from langchain_core.callbacks import BaseCallbackHandler
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

class WebSocketCallbackHandler(BaseCallbackHandler):
    def __init__(self, group_name):
        self.group_name = group_name
        self.channel_layer = get_channel_layer()
        self.run_id = None

    def on_chain_start(self, serialized, inputs, run_id, **kwargs):
        self.run_id = run_id
        async_to_sync(self.channel_layer.group_send)(
            self.group_name,
            {
                "type": "chat_message",
                "event": "start",
                "run_id": run_id,
            }
        )

    def on_llm_new_token(self, token: str, **kwargs):
        async_to_sync(self.channel_layer.group_send)(
            self.group_name,
            {
                "type": "chat_message",
                "event": "stream",
                "run_id": self.run_id,
                "token": token,
            }
        )

    def on_chain_end(self, outputs, **kwargs):
        async_to_sync(self.channel_layer.group_send)(
            self.group_name,
            {
                "type": "chat_message",
                "event": "end",
                "run_id": self.run_id,
                "output": outputs.get("output", "")
            }
        )

