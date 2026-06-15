from typing import Any, Dict, Optional

from enthusiast_common.repositories import BaseConversationRepository
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import AIMessage, BaseMessage, ToolMessage, messages_from_dict

from agent.models import Message


class PersistentChatHistory(BaseChatMessageHistory):
    """
    A chat history implementation that persists messages in the database.
    Inject it into the agent to enable conversation persistence.
    """

    def __init__(self, conversation_repo: BaseConversationRepository, conversation_id: Any):
        self._conversation = conversation_repo.get_by_id(conversation_id)

    def add_messages(self, messages: list[BaseMessage]) -> None:
        """Persist messages, interleaving each tool call with its result.

        LLMs can invoke tools in parallel, producing an AIMessage with multiple tool_calls
        followed by multiple ToolMessages. This reorders them so each tool call is immediately
        followed by its result, which allows straightforward one-to-one reconstruction.
        """
        tool_messages = {m.tool_call_id: m for m in messages if isinstance(m, ToolMessage)}
        for message in messages:
            if isinstance(message, AIMessage) and message.tool_calls:
                for tool_call in message.tool_calls:
                    self.add_message(AIMessage(content="", tool_calls=[tool_call]))
                    if tool_call["id"] in tool_messages:
                        self.add_message(tool_messages[tool_call["id"]])
            elif isinstance(message, ToolMessage):
                pass  # already persisted paired with its tool call above
            else:
                self.add_message(message)

    def add_message(self, message: BaseMessage) -> None:
        """Persist a message to the database.

        AIMessages that contain tool calls are stored as INTERMEDIATE_STEP records.
        ToolMessages (tool results) are stored as FUNCTION records.
        All other standard message types are stored using their LangChain type string directly.
        """
        if isinstance(message, AIMessage) and message.tool_calls:
            self._create_intermediate_step_message(message)
        elif isinstance(message, ToolMessage):
            self.create_tool_message(message)
        else:
            self._conversation.messages.create(
                type=message.type,
                text=message.text,
                function_name=getattr(message, "name", None),
            )

    def _create_intermediate_step_message(self, message: AIMessage) -> None:
        for tool_call in message.tool_calls:
            text = f"Invoking `{tool_call['name']}` with `{tool_call['args']}`."
            self._conversation.messages.create(
                type=Message.MessageType.INTERMEDIATE_STEP,
                text=text,
                function_name=tool_call["name"],
                tool_call_id=tool_call["id"],
            )

    def create_tool_message(self, message: ToolMessage) -> None:
        self._conversation.messages.create(
            type=Message.MessageType.FUNCTION,
            text=message.text,
            function_name=message.name,
            tool_call_id=message.tool_call_id,
        )

    @property
    def messages(self) -> list[BaseMessage]:
        messages = list(self._conversation.messages.filter(answer_failed=False).order_by("id"))
        message_dicts = []
        for msg in messages:
            message_dicts.append(self._parse_message_to_dict(msg))
        return messages_from_dict(message_dicts)

    @property
    def last_message_database_id(self) -> Optional[int]:
        """Return the DB primary key of the most recent message in this conversation, or None."""
        last = self._conversation.messages.filter(answer_failed=False).order_by("id").last()
        return last.id if last else None

    def messages_after(self, message_id: Optional[int]) -> list[BaseMessage]:
        """Return messages after the given message ID.

        If message_id is None, returns all messages. Used by the memory compactor to fetch
        only messages that have not yet been included in the conversation summary.
        """
        queryset = self._conversation.messages.filter(answer_failed=False).order_by("id")
        if message_id is not None:
            queryset = queryset.filter(id__gt=message_id)
        db_messages = list(queryset)
        if not db_messages:
            return []
        return messages_from_dict([self._parse_message_to_dict(m) for m in db_messages])

    @staticmethod
    def _parse_message_to_dict(message: BaseMessage) -> Dict[str, Any]:
        data: Dict[str, Any] = {"content": message.text, "name": message.function_name}
        match message.type:
            case Message.MessageType.INTERMEDIATE_STEP:
                data = {
                    "content": message.text,
                    "tool_calls": [{"id": message.tool_call_id, "name": message.function_name or "", "args": {}}],
                }
            case Message.MessageType.FUNCTION:
                data = {"content": message.text, "name": message.function_name, "tool_call_id": message.tool_call_id}
        return {"type": message.langchain_type, "data": data}

    def clear(self) -> None:
        self._conversation.messages.all().delete()
