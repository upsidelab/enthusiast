from abc import ABC, abstractmethod, ABCMeta
from typing import Any

from enthusiast_common.connectors import ECommercePlatformConnector
from enthusiast_common.structures import DocumentDetails, ProductDetails
from enthusiast_common.utils import validate_required_vars, RequiredFieldsModel


class ExtraArgsClassBaseMeta(ABCMeta):
    REQUIRED_VARS = {}

    def __new__(mcs, name, bases, namespace, **kwargs):
        cls = super().__new__(mcs, name, bases, namespace, **kwargs)
        if not namespace.get("__abstract__", False):
            return validate_required_vars(cls, name, cls.REQUIRED_VARS)
        return cls


class SourceExtraArgsClassBaseMeta(ExtraArgsClassBaseMeta):
    REQUIRED_VARS = {
        "CONFIGURATION_ARGS": RequiredFieldsModel,
    }


class SourceExtraArgsClassBase(metaclass=SourceExtraArgsClassBaseMeta):
    __abstract__ = True

    def set_runtime_arguments(self, runtime_arguments: Any) -> None:
        for key, value in runtime_arguments.items():
            class_field_key = key.upper()
            field = getattr(self, class_field_key)
            if field is None:
                continue
            setattr(self, key.upper(), field(**value))


class ProductSourcePlugin(ABC, SourceExtraArgsClassBase):
    CONFIGURATION_ARGS = None

    def __init__(self, data_set_id):
        self.data_set_id = data_set_id

    @abstractmethod
    def fetch(self) -> list[ProductDetails]:
        """Fetches products from an external source.

        Returns:
            list[ProductDetails]: A list of products to be imported to the database
        """
        pass


class DocumentSourcePlugin(ABC, SourceExtraArgsClassBase):
    CONFIGURATION_ARGS = None

    def __init__(self, data_set_id):
        self.data_set_id = data_set_id

    @abstractmethod
    def fetch(self) -> list[DocumentDetails]:
        """Fetches documents from an external system.

        Returns:
            list[DocumentDetails]: A list of documents to be imported to the database
        """
        pass


class ECommerceIntegrationPlugin(ABC, SourceExtraArgsClassBase):
    NAME: str = None
    CONFIGURATION_ARGS = None

    def __init__(self, data_set_id):
        self.data_set_id = data_set_id

    @abstractmethod
    def build_connector(self) -> ECommercePlatformConnector:
        """Provides a connector for the e-commerce platform.

        Returns:
            ECommercePlatformConnector: A connector for interacting with the e-commerce platform
        """
        pass

    @abstractmethod
    def build_product_source(self) -> ProductSourcePlugin:
        """Provides a product source for syncing and indexing products from the e-commerce platform.

        Returns:
            ProductSourcePlugin: A product source for fetching product data from the e-commerce platform.
        """
