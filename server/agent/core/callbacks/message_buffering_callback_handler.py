from typing import Any
from uuid import UUID

from agent.core.callbacks.conversation_websocket_callback_handler import ConversationWebSocketCallbackHandler


class MessageBufferingCallbackHandler(ConversationWebSocketCallbackHandler):
    """Callback handler that buffers LLM tokens for a full run before sending.

    Some LLM providers emit text tokens before tool calls within the same run,
    making it impossible to filter pre-tool text in ``on_llm_new_token`` alone.
    This handler defers streaming until ``on_llm_end``, sending the complete
    response only when no tool calls were made.

    Inject this handler instead of ``ConversationWebSocketCallbackHandler``
    for providers that require it (see ``LanguageModelProvider.STREAMING_REQUIRES_MESSAGE_BUFFERING``).
    """

    def __init__(self, conversation_id: int):
        super().__init__(conversation_id)
        self._buffering_runs: set[UUID] = set()

    def on_chat_model_start(self, serialized: dict, messages: list, *, run_id: UUID, **kwargs):
        self._buffering_runs.add(run_id)

    def on_llm_new_token(self, token: str | list, *, run_id: UUID, **kwargs):
        if run_id in self._buffering_runs:
            return
        super().on_llm_new_token(token, run_id=run_id, **kwargs)

    def on_llm_end(self, response: Any, *, run_id: UUID, **kwargs):
        if run_id not in self._buffering_runs:
            return
        self._buffering_runs.discard(run_id)
        generation = response.generations[0][0] if response.generations else None
        if not generation or not hasattr(generation, "message") or generation.message.tool_calls:
            return
        if text := generation.message.text:
            self.send_message({"type": "chat_message", "event": "stream", "token": text})
