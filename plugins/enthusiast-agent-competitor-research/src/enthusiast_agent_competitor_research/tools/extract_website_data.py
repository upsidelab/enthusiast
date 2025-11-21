import logging

import requests
from bs4 import BeautifulSoup
from enthusiast_common.config.prompts import ChatPromptTemplateConfig, Message, MessageRole
from enthusiast_common.tools import BaseLLMTool
from enthusiast_common.utils import RequiredFieldsModel
from pydantic import BaseModel, Field
from requests import HTTPError

logger = logging.getLogger(__name__)


EXTRACT_DATA_PROMPT = """
Your goal is to extract exactly those values {keys}
from this web scraped data: {input}.
Focus only on main product.
"""


class ExtractWebsiteDataToolInput(BaseModel):
    url: str = Field(description="web page url")
    parameters_to_extract: str = Field(description="comma separated list of parameter's names to extract")


class ExtractWebsiteDataToolConfigurationArgs(RequiredFieldsModel):
    proxy: str = Field(title="Proxy", description="proxy address to use when requesting webpage data.", default="")


class ExtractWebsiteDataTool(BaseLLMTool):
    NAME = "extract_website_data_tool"
    DESCRIPTION = "It's tool for extracting data from web page"
    ARGS_SCHEMA = None
    RETURN_DIRECT = False
    CONFIGURATION_ARGS = ExtractWebsiteDataToolConfigurationArgs

    def run(self, url: str, parameters_to_extract: str) -> str:
        try:
            response = requests.get(url, proxies=self._get_proxies())
            response.raise_for_status()

            html = response.text
            soup = BeautifulSoup(html, "html.parser")
            page_text = soup.get_text(separator="\n", strip=True)
            results = self._extract_from_text(page_text, parameters_to_extract)
            return results
        except HTTPError:
            return "Could not reach provided webpage."
        except Exception as e:
            logger.error(e)
            return "Internal error - could not extract data."

    def _extract_from_text(self, data: str, parameters_to_extract: str) -> str:
        chat_prompt_template_config = ChatPromptTemplateConfig(
            messages=[
                Message(
                    role=MessageRole.SYSTEM,
                    content=EXTRACT_DATA_PROMPT,
                ),
            ]
        )
        chat_prompt_template = chat_prompt_template_config.to_chat_prompt_template()
        messages = chat_prompt_template.format_messages(input=data, keys=parameters_to_extract)

        return self._llm.invoke(messages).content

    def _get_proxies(self) -> dict | None:
        if self.CONFIGURATION_ARGS.proxy:
            return {
                "http": self.CONFIGURATION_ARGS.proxy,
                "https": self.CONFIGURATION_ARGS.proxy,
            }
        return None
