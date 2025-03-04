import logging

from enthusiast_common.interfaces import LanguageModelProvider

from agent.models import Conversation
from .registry import ToolRegistry

logger = logging.getLogger(__name__)

class ToolManager:
    def __init__(self, language_model_provider: LanguageModelProvider, conversation: Conversation):
        self.conversation = conversation
        self.registry = ToolRegistry()
        self.tools = self.registry.get_tools(language_model_provider=language_model_provider, conversation=conversation)
