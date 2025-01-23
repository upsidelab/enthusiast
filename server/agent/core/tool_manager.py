import importlib
import logging
from .tool_registry import ToolRegistry

logger = logging.getLogger(__name__)

class ToolManager:
    def __init__(self, data_set, chat_model):
        self.data_set = data_set
        self.chat_model = chat_model
        self.registry = ToolRegistry()
        self.tools = self._initialize_tools()

    def _initialize_tools(self):
        tools = []
        for tool_name, module_path in self.registry.get_plugins():
            module_name, class_name = module_path.rsplit('.', 1)
            try:
                module = importlib.import_module(module_name)
                tool_class = getattr(module, class_name)
                tool_instance = tool_class(data_set=self.data_set, chat_model=self.chat_model)
                tools.append(tool_instance)
            except ModuleNotFoundError as e:
                logger.error(f"Module {module_name} not found: {e}")
            except AttributeError as e:
                logger.error(f"Class {class_name} not found in module {module_name}: {e}")
        return tools