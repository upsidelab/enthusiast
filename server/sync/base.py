from abc import ABC, abstractmethod
from importlib import import_module
from dataclasses import dataclass
from common.plugin.interface import ItemData


@dataclass
class DataSetPlugin:
    """Represents configuration of plugin."""
    data_set_id: int
    config: str


class SourcePluginRegistry(ABC):
    """Registry of source plugins."""

    def __init__(self):
        self.plugins = self.load_plugins()

    def load_plugins(self):
        plugins = []
        for plugin_name, plugin_path in self.get_plugins():
            module_name, class_name = plugin_path.rsplit(".", 1)
            module = import_module(module_name)
            plugin_class = getattr(module, class_name)
            # Get configuration and instantiate.
            data_set_plugin = self.get_data_set_config(plugin_name)
            plugin = plugin_class(data_set_plugin.data_set_id, data_set_plugin.config)
            plugins.append(plugin)
        return plugins

    @abstractmethod
    def get_plugins(self) -> dict:
        pass

    @abstractmethod
    def get_data_set_config(self, plugin_name) -> DataSetPlugin:
        pass


class SyncManager(ABC):
    """Orchestrates synchronisation activities of registered plugins."""

    def __init__(self):
        self.registry = self._build_registry()

    def sync_all_plugins(self):
        for plugin in self.registry.plugins:
            self.sync_plugin(plugin)

    def sync_plugin(self, plugin):
        for element_data in plugin.fetch():
            self._sync_item(plugin.data_set_id, element_data)

    @abstractmethod
    def _build_registry(self):
        pass

    @abstractmethod
    def _sync_item(self, data_set_id: int, item_data: ItemData):
        """Creates an item in the database.

        Args:
            data_set_id (int): obligatory, a data set to which imported data belongs to.
            item_data (dict): item details.
        """
        pass