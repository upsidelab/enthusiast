from agent.core.callbacks.base_websocket_handler import BaseWebSocketHandler


class ConversationWebSocketCallbackHandler(BaseWebSocketHandler):
    """Streams LLM tokens to the WebSocket group for a conversation."""

    def on_llm_new_token(self, token: str, **kwargs):
        if not token:
            return
        self.send_message({"type": "chat_message", "event": "stream", "token": token})
