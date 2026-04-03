from typing import Optional
from uuid import UUID

from agent.core.callbacks.base_websocket_handler import BaseWebSocketHandler


class ConversationWebSocketCallbackHandler(BaseWebSocketHandler):
    """Streams LLM tokens to the WebSocket group for a conversation."""

    def on_llm_new_token(self, token: str | list, *, run_id: UUID, **kwargs):
        token = self._prepare_token(token)
        if token:
            self.send_message({"type": "chat_message", "event": "stream", "token": token})

    @staticmethod
    def _prepare_token(token: str | list) -> Optional[str]:
        if not token:
            return None
        return token[0].get("text") if isinstance(token, list) else token
