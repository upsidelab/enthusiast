from .connectors import ECommercePlatformConnector
from .interfaces import DocumentSourcePlugin, ECommerceIntegrationPlugin, ProductSourcePlugin
from .structures import Address, DocumentDetails, ProductDetails, ProductUpdateDetails

__all__ = [
    "Address",
    "DocumentDetails",
    "DocumentSourcePlugin",
    "ECommercePlatformConnector",
    "ECommerceIntegrationPlugin",
    "ProductDetails",
    "ProductSourcePlugin",
    "ProductUpdateDetails",
]
