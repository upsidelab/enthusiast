import importlib
import logging
from django.conf import settings

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
            module_name, class_name = module_path.rsplit('.', 1)
            module = importlib.import_module(module_name)
            tool_class = getattr(module, class_name)
            tool_classes[tool_name] = tool_class
        return tool_classes

    def get_tools(self, chat_model, conversation):
        """
        Instantiate tool classes with the provided data_set and chat_model.

        Args:
            chat_model (str): The chat model used by the tools.
            conversation (Conversation): The conversation object.

        Returns:
            list: A list of instantiated tool objects.
        """
        tools = []
        for tool_name, tool_class in self.tool_classes.items():
            # Instantiate the tool class with the provided arguments
            tool_instance = tool_class(chat_model=chat_model, conversation=conversation)
            # Add the instantiated tool to the list
            tools.append(tool_instance)
        return tools