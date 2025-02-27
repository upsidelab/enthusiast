import logging
from .registry import ToolRegistry

logger = logging.getLogger(__name__)

class ToolManager:
    def __init__(self, chat_model, conversation):
        self.conversation = conversation
        self.data_set = conversation.data_set
        self.chat_model = chat_model
        self.registry = ToolRegistry()
        self.tools = self.registry.get_tools(chat_model=self.chat_model, conversation=self.conversation)