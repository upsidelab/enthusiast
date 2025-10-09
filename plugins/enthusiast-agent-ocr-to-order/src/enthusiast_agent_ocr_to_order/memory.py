import typing
from abc import ABC
from typing import Any, Dict

from enthusiast_common.repositories import BaseConversationRepository
from enthusiast_common.structures import LLMFile
from langchain.memory import ConversationBufferMemory, ConversationSummaryBufferMemory, ConversationTokenBufferMemory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import AIMessage, BaseMessage, FunctionMessage, HumanMessage, messages_from_dict


class PersistentChatHistory(BaseChatMessageHistory):
    """
    A chat history implementation that persists messages in the database.
    Inject it to agent's memory, to enable conversation persistence.
    """

    def __init__(self, conversation_repo: BaseConversationRepository, conversation_id: Any):
        self._conversation = conversation_repo.get_by_id(conversation_id)

    def add_message(self, message: BaseMessage) -> None:
        self._conversation.messages.create(
            role=message.type,
            text=message.content,
            file_id=getattr(message, "file_id", None),
            name=getattr(message, "name", ""),
        )

    @property
    def messages(self) -> list[BaseMessage]:
        messages = self._conversation.messages.filter(answer_failed=False, file_id__isnull=True).order_by("created_at")
        message_dicts = [
            {"type": message.role, "data": {"content": message.text, "name": message.name}} for message in messages
        ]
        return messages_from_dict(message_dicts)

    def get_files(self) -> list[LLMFile]:
        messages = self._conversation.messages.filter(answer_failed=False, file_id__isnull=False).order_by("created_at")
        files = [self._conversation.files.filter(pk=message.file_id).first() for message in messages]
        return [file.get_llm_file_object() for file in files]

    def clear(self) -> None:
        self._conversation.messages.all().delete()


class UploadedFile(HumanMessage):
    file_id: bool = True


class PersistIntermediateStepsMixin(ABC):
    """
    This mixin can be added to a ConversationBufferMemory class in order to persist agent's function calls.
    """

    def save_context(self, inputs: Dict[str, Any], outputs: Dict[str, str]) -> None:
        self_as_conversation_memory = typing.cast(ConversationBufferMemory, self)

        human_message = HumanMessage(inputs["input"])
        self_as_conversation_memory.chat_memory.add_message(human_message)

        if "intermediate_steps" in outputs:
            for agent_action, result in outputs["intermediate_steps"]:
                self_as_conversation_memory.chat_memory.add_message(agent_action.messages[0])

                function_message = FunctionMessage(name=agent_action.tool, content=result)
                self_as_conversation_memory.chat_memory.add_message(function_message)

        ai_message = AIMessage(outputs["output"])
        self_as_conversation_memory.chat_memory.add_message(ai_message)


class LimitedChatMemory(PersistIntermediateStepsMixin, ConversationTokenBufferMemory):
    """
    This memory persists intermediate steps, and limits the amount of tokens passed back to the agent to
    what's defined as max_token_limit.
    """

    pass


class SummaryChatMemory(PersistIntermediateStepsMixin, ConversationSummaryBufferMemory):
    """
    This memory persists intermediate steps, and summarizes the history passed back to the agent if the history
    exceeds the token limit.
    """

    pass
