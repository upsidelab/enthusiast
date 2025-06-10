from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

from ..repositories import (
    BaseConversationRepository,
    BaseMessageRepository,
    BaseUserRepository,
)

T = TypeVar("T")


class BaseConversationService(ABC, Generic[T]):
    def __init__(
        self,
        conversation_repo: BaseConversationRepository,
        message_repo: BaseMessageRepository,
        user_repo: BaseUserRepository,
    ):
        self.conversation_repo = conversation_repo
        self.message_repo = message_repo
        self.user_repo = user_repo

    @abstractmethod
    def create_conversation(self, user_id: int, data_set_id: int) -> T:
        pass

    @abstractmethod
    def save_user_message(self, conversation_id: int, message: str):
        pass

    @abstractmethod
    def get_messages(self, conversation_id: int) -> list[Any]:
        pass

    @abstractmethod
    def record_error(self, conversation_id: int):
        pass
