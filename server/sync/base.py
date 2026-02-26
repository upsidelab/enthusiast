from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generic, List, Type, TypeVar

from utils.base_registry import BaseRegistry


@dataclass
class DataSetSource:
    """Represents configuration of a data set source."""

    plugin_name: str
    data_set_id: int
    config: dict


T = TypeVar("T")


class SourcePluginRegistry(BaseRegistry[T]):
    """Registry of available source plugins registered in ECL system.

    Subclasses must implement ``_get_plugin_paths`` to return the list of
    class paths from Django settings.
    """

    def get_plugin_classes(self) -> List[Type[T]]:
        """Returns all plugin classes registered in settings."""
        return [self._get_plugin_class_by_path(path) for path in self._get_plugin_paths()]

    def _get_plugin_classes_by_names(self) -> dict[str, Type[T]]:
        """Returns a mapping of plugin NAME to plugin class."""
        return {plugin_class.NAME: plugin_class for plugin_class in self.get_plugin_classes()}

    def get_plugin_class_by_name(self, name: str) -> Type[T]:
        """Looks up a plugin class by its NAME attribute."""
        return self._get_plugin_classes_by_names()[name]

    def get_plugin_instance(self, source) -> T:
        """Creates a configured instance of a plugin.

        Args:
            source: An object with ``plugin_name``, ``data_set_id``, and ``config`` attributes.

        Returns:
            A plugin instance configured to fetch data from an external source.
        """
        plugin_class = self.get_plugin_class_by_name(source.plugin_name)
        plugin_instance = plugin_class(data_set_id=source.data_set_id)
        plugin_instance.set_runtime_arguments(source.config)
        return plugin_instance

    @staticmethod
    @abstractmethod
    def _get_plugin_paths() -> List[str]:
        """Returns the list of plugin class paths from settings."""
        pass


class SyncManager(ABC, Generic[T]):
    """Orchestrates synchronisation activities of registered plugins."""

    def __init__(self):
        self.registry = self._build_registry()

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
