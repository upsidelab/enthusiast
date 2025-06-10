import importlib
import logging
from django.conf import settings
from enthusiast_common.interfaces import LanguageModelProvider

from catalog.models import DataSet

logger = logging.getLogger(__name__)


class ToolRegistry:
    def __init__(self):
        self.tool_classes = self._load_tool_classes()

    def _load_tool_classes(self):
        """
        Load tool classes based on the configuration in settings.AGENT_TOOLS.

        Returns:
            dict: A dictionary where the keys are tool names and the values are the corresponding tool classes.
        """
        tool_classes = {}
        for tool_name, module_path in settings.AGENT_TOOLS.items():
            module_name, class_name = module_path.rsplit(".", 1)
            module = importlib.import_module(module_name)
            tool_class = getattr(module, class_name)
            tool_classes[tool_name] = tool_class
        return tool_classes

    def get_tools(self, data_set: DataSet, language_model_provider: LanguageModelProvider):
        """
        Instantiate tool classes with the provided data_set and chat_model.

        Args:
            data_set (DataSet): The data set used by the tools.
            language_model_provider (LanguageModelProvider): The chat model used by the tools.

        Returns:
            list: A list of instantiated tool objects.
        """
        tools = []
        for tool_name, tool_class in self.tool_classes.items():
            tool_instance = tool_class(
                data_set=data_set, chat_model=None, language_model_provider=language_model_provider
            )
            tools.append(tool_instance)
        return tools
