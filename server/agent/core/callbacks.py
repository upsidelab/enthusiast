from typing import Any, Optional
from uuid import UUID

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
    def __init__(self, conversation_id: int):
        super().__init__(conversation_id)
        self._buffering_runs: set[UUID] = set()  # Anthropic workaround — see below

    def on_llm_new_token(self, token: str | list, *, run_id: UUID, **kwargs):
        if run_id in self._buffering_runs:
            # Anthropic emits text tokens before tool calls in the same run — defer sending until on_llm_end confirms no tool calls were made
            return
        token = self._prepare_token(token)
        if token:
            self.send_message({"type": "chat_message", "event": "stream", "token": token})

    @staticmethod
    def _prepare_token(token: str | list) -> Optional[str]:
        if not token:
            return None
        return token[0].get("text") if isinstance(token, list) else token

    # --- Anthropic workaround ---
    # Anthropic models emit text tokens before tool calls within the same LLM run,
    # making it impossible to filter them in on_llm_new_token without buffering.
    # The full response text is streamed from on_llm_end only if no tool calls were made.

    def on_chat_model_start(self, serialized: dict, messages: list, *, run_id: UUID, **kwargs):
        ids = serialized.get("id", [])
        if any("anthropic" in part.lower() for part in ids):
            self._buffering_runs.add(run_id)

    def on_llm_end(self, response: Any, *, run_id: UUID, **kwargs):
        if run_id not in self._buffering_runs:
            return
        self._buffering_runs.discard(run_id)
        generation = response.generations[0][0] if response.generations else None
        if not generation or not hasattr(generation, "message") or generation.message.tool_calls:
            return
        if text := generation.message.content:
            self.send_message({"type": "chat_message", "event": "stream", "token": text})