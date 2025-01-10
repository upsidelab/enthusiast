from importlib import import_module

from enthusiast_common.interfaces import LanguageModelProvider

from catalog.models import DataSet
from pecl import settings


class LanguageModelRegistry:
    def __init__(self):
        self._providers = settings.CATALOG_LANGUAGE_MODEL_PROVIDERS

    def provider_for_dataset(self, data_set: DataSet) -> LanguageModelProvider:
        provider_class_name = self._providers[data_set.language_model_provider]
        module_name, class_name = provider_class_name.rsplit(".", 1)
        module = import_module(module_name)
        provider_class = getattr(module, class_name)
        return provider_class(data_set.language_model_name)