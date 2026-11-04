from typing import Optional

from enthusiast_vertical_common.connectors import ECommercePlatformConnector
from suvereo_common.injectors import Injector

from enthusiast_vertical.retrievers import DocumentRetriever, ProductRetriever


class EcommerceInjector(Injector):
    """Extends the framework Injector with ecommerce-specific retrievers and the platform connector."""

    def __init__(
        self,
        *args,
        product_retriever: ProductRetriever,
        document_retriever: DocumentRetriever,
        ecommerce_platform_connector: Optional[ECommercePlatformConnector] = None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self._product_retriever = product_retriever
        self._document_retriever = document_retriever
        self._ecommerce_platform_connector = ecommerce_platform_connector

    @property
    def product_retriever(self) -> ProductRetriever:
        return self._product_retriever

    @property
    def document_retriever(self) -> DocumentRetriever:
        return self._document_retriever

    @property
    def ecommerce_platform_connector(self) -> Optional[ECommercePlatformConnector]:
        return self._ecommerce_platform_connector
