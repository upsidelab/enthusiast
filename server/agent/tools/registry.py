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
            try:
                module = importlib.import_module(module_name)
                tool_class = getattr(module, class_name)
                tool_classes[tool_name] = tool_class
            except ModuleNotFoundError as e:
                # Log an error if the module is not found
                logger.error(f"Module {module_name} not found: {e}")
            except AttributeError as e:
                # Log an error if the class is not found in the module
                logger.error(f"Class {class_name} not found in module {module_name}: {e}")
        return tool_classes

    def get_tools(self, data_set, chat_model):
        """
        Instantiate tool classes with the provided data_set and chat_model.

        Args:
            data_set (Any): The dataset used by the tools.
            chat_model (str): The chat model used by the tools.

        Returns:
            list: A list of instantiated tool objects.
        """
        tools = []
        for tool_name, tool_class in self.tool_classes.items():
            try:
                # Instantiate the tool class with the provided arguments
                tool_instance = tool_class(data_set=data_set, chat_model=chat_model)
                # Add the instantiated tool to the list
                tools.append(tool_instance)
            except Exception as e:
                # Log an error if there is an issue initializing the tool
                logger.error(f"Error initializing tool {tool_name}: {e}")
        return tools