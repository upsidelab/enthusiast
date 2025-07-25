from abc import ABC, abstractmethod
from typing import Any

from langchain_core.callbacks import BaseCallbackHandler


class ConversationCallbackHandler(ABC, BaseCallbackHandler):
    @abstractmethod
    def send_message(self, message_data: Any) -> None:
        pass
