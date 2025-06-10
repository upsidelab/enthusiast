from abc import ABC, abstractmethod
from dataclasses import dataclass
from importlib import import_module
from typing import Generic, TypeVar


@dataclass
class DataSetSource:
    """Represents configuration of a data set source."""

    plugin_name: str
    data_set_id: int
    config: dict


T = TypeVar("T")


class SourcePluginRegistry(ABC):
    """Registry of available source plugins registered in ECL system."""

    def __init__(self):
        self.plugins = self.load_plugins()

    def load_plugins(self):
        plugins = {}
        for plugin_name, plugin_path in self.get_plugins():
            module_name, class_name = plugin_path.rsplit(".", 1)
            module = import_module(module_name)
            plugin_class = getattr(module, class_name)
            plugins[plugin_name] = plugin_class
        return plugins

    def get_plugin_instance(self, data_set_source: DataSetSource):
        """Creates an instance of catalog item source.

        Args:
            data_set_source (DataSetSource): configuration of a plugin for a data set.

        Returns:
            Instance of a plugin that is configured to fetch data from external source and load to a given dataset.
        """
        plugin_class = self.plugins[data_set_source.plugin_name]
        return plugin_class(data_set_id=data_set_source.data_set_id, config=data_set_source.config)

    @abstractmethod
    def get_plugins(self) -> dict:
        pass


class SyncManager(ABC, Generic[T]):
    """Orchestrates synchronisation activities of registered plugins."""

    def __init__(self):
        self.registry = self._build_registry()

    def sync_all(self):
        for source in self._get_all_sources():
            self.sync_plugin(source)

    def sync_data_set(self, data_set_id: int):
        for source in self._get_data_set_sources(data_set_id=data_set_id):
            self.sync_plugin(source)

    def sync(self, source_id: int):
        source = self._get_data_set_source(source_id)
        self.sync_plugin(source)

    def sync_plugin(self, source: DataSetSource):
        plugin = self.registry.get_plugin_instance(source)
        for item_data in plugin.fetch():
            self._sync_item(data_set_id=plugin.data_set_id, item_data=item_data)

    @abstractmethod
    def _build_registry(self):
        pass

    @abstractmethod
    def _get_all_sources(self) -> list[DataSetSource]:
        pass

    @abstractmethod
    def _get_data_set_sources(self, data_set_id: int) -> list[DataSetSource]:
        pass

    @abstractmethod
    def _get_data_set_source(self, source_id: int) -> DataSetSource:
        pass

    @abstractmethod
    def _sync_item(self, data_set_id: int, item_data: T):
        """Creates an item in the database.

        Args:
            data_set_id (int): obligatory, a data set to which imported data belongs to.
            item_data (T): item details.
        """
        pass
