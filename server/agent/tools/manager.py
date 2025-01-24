import logging
from .registry import ToolRegistry

logger = logging.getLogger(__name__)

class ToolManager:
    def __init__(self, data_set, chat_model):
        self.data_set = data_set
        self.chat_model = chat_model
        self.registry = ToolRegistry()
        self.tools = self.registry.get_tools(data_set=self.data_set, chat_model=self.chat_model)
