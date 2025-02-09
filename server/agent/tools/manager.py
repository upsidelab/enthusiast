import logging

from enthusiast_common.interfaces import LanguageModelProvider

from catalog.models import DataSet
from .registry import ToolRegistry

logger = logging.getLogger(__name__)

class ToolManager:
    def __init__(self, data_set: DataSet, language_model_provider: LanguageModelProvider):
        self.registry = ToolRegistry()
        self.tools = self.registry.get_tools(data_set=data_set, language_model_provider=language_model_provider)
