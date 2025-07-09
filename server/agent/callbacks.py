from typing import Any, Optional
from uuid import UUID

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from langchain_core.agents import AgentAction
from langchain_core.callbacks import BaseCallbackHandler


class BaseWebSocketCallbackHandler(BaseCallbackHandler):
    def __init__(self, conversation_id: int):
        self.group_name = f"conversation_{conversation_id}"
        self.channel_layer = get_channel_layer()
        self.run_id = None


class ConversationWebSocketCallbackHandler(BaseWebSocketCallbackHandler):
    def on_chain_start(self, serialized, inputs, run_id, **kwargs):
        self.run_id = run_id
        async_to_sync(self.channel_layer.group_send)(
            self.group_name,
            {
                "type": "chat_message",
                "event": "start",
                "run_id": run_id,
            },
        )

    def on_llm_new_token(self, token: str, **kwargs):
        async_to_sync(self.channel_layer.group_send)(
            self.group_name,
            {
                "type": "chat_message",
                "event": "stream",
                "run_id": self.run_id,
                "token": token,
            },
        )

    def on_chain_end(self, outputs, **kwargs):
        async_to_sync(self.channel_layer.group_send)(
            self.group_name,
            {"type": "chat_message", "event": "end", "run_id": self.run_id, "output": outputs.get("output")},
        )


class ReactAgentWebsocketCallbackHandler(ConversationWebSocketCallbackHandler):
    def __init__(self, conversation):
        super().__init__(conversation)
        self.first_final_answer_chunk = False
        self.second_final_answer_chunk = False
        self.third_final_answer_chunk = False

    def _restore_final_answer_chunks(self):
        self.first_final_answer_chunk = False
        self.second_final_answer_chunk = False
        self.third_final_answer_chunk = False

    def _is_final_answer_chunk(self, chunk: str):
        chunk = chunk.strip(" ").lower()
        if not self.first_final_answer_chunk:
            if not chunk == "final":
                self._restore_final_answer_chunks()
            else:
                self.first_final_answer_chunk = True
            return False
        elif not self.second_final_answer_chunk:
            if not chunk == "answer":
                self._restore_final_answer_chunks()
            else:
                self.second_final_answer_chunk = True
            return False
        elif not self.third_final_answer_chunk:
            if not chunk == ":":
                self._restore_final_answer_chunks()
            else:
                self.third_final_answer_chunk = True
            return False
        else:
            return True

    def on_llm_new_token(self, token: str, **kwargs):
        if self._is_final_answer_chunk(token):
            async_to_sync(self.channel_layer.group_send)(
                self.group_name,
                {
                    "type": "chat_message",
                    "event": "stream",
                    "run_id": self.run_id,
                    "token": token,
                },
            )


class AgentActionWebsocketCallbackHandler(BaseWebSocketCallbackHandler):
    def on_agent_action(
        self,
        action: AgentAction,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> Any:
        output = action.log.split("Action:")[0]
        output = output.split("Thought:")[-1]
        output = output.strip()
        async_to_sync(self.channel_layer.group_send)(
            self.group_name,
            {
                "type": "chat_message",
                "event": "action",
                "run_id": self.run_id,
                "output": output,
            },
        )
