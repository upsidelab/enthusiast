from pydantic import Field

from enthusiast_common.connectors import BaseECommercePlatformConnector
from enthusiast_common.connectors.medusa_platform_connector import MedusaPlatformConnector
from enthusiast_common.interfaces import ECommerceIntegrationPlugin
from enthusiast_common.utils import RequiredFieldsModel


class MedusaIntegrationConfig(RequiredFieldsModel):
    base_url: str = Field(description="Medusa API URL")
    api_key: str = Field(description="Medusa API Key")

class MedusaIntegration(ECommerceIntegrationPlugin):
    NAME = "Medusa"
    CONFIGURATION_ARGS = MedusaIntegrationConfig

    def build_connector(self) -> BaseECommercePlatformConnector:
        return MedusaPlatformConnector(base_url=self.CONFIGURATION_ARGS.base_url, api_key=self.CONFIGURATION_ARGS.api_key)
