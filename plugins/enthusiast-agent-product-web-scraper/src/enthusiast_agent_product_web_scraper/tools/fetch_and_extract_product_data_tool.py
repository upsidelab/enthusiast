import logging

import requests
from bs4 import BeautifulSoup
from enthusiast_common.tools import BaseLLMTool
from enthusiast_common.utils import RequiredFieldsModel
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from requests import HTTPError

logger = logging.getLogger(__name__)

_MINIMAL_CONTENT_THRESHOLD = 300
_REQUEST_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

EXTRACT_DATA_PROMPT = """
Your goal is to extract exactly these fields: {keys}
from the following web page content: {input}.
Focus only on the main product described on the page.
Return only the extracted values — no explanation, no extra keys.
"""


class FetchAndExtractProductDataToolInput(BaseModel):
    """Input schema for FetchAndExtractProductDataTool."""

    url: str = Field(description="URL of the product web page to fetch and extract data from")
    parameters_to_extract: str = Field(
        description="Comma-separated list of field names to extract from the page (e.g. 'sku, name, description, price')"
    )


class FetchAndExtractProductDataToolConfigurationArgs(RequiredFieldsModel):
    """Runtime configuration for FetchAndExtractProductDataTool."""

    proxy: str = Field(
        title="Proxy",
        description="Optional proxy address to use when fetching web pages (e.g. 'http://proxy:8080'). Leave empty to fetch directly.",
        default="",
    )


class FetchAndExtractProductDataTool(BaseLLMTool):
    """Fetches a product web page and extracts structured product data from it using an LLM.

    Uses plain HTTP requests and BeautifulSoup for content extraction. JavaScript-rendered
    pages (SPAs) may return minimal content — in that case the tool returns a warning so the
    agent can relay it to the user.
    """

    NAME = "fetch_and_extract_product_data"
    DESCRIPTION = (
        "Fetches a product web page from the given URL and extracts specified product fields "
        "from its content. Provide the URL and a comma-separated list of field names to extract. "
        "Does not support JavaScript-rendered pages — static HTML only."
    )
    ARGS_SCHEMA = FetchAndExtractProductDataToolInput
    RETURN_DIRECT = False
    CONFIGURATION_ARGS = FetchAndExtractProductDataToolConfigurationArgs

    def run(self, url: str, parameters_to_extract: str) -> str:
        """Fetch the page at `url` and extract the requested fields via LLM.

        Args:
            url: The product page URL to scrape.
            parameters_to_extract: Comma-separated field names to extract.

        Returns:
            Extracted field values as a string, or an informative error/warning message.
        """
        try:
            response = requests.get(url, headers=_REQUEST_HEADERS, proxies=self._get_proxies(), timeout=15)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            page_text = soup.get_text(separator="\n", strip=True)

            if len(page_text) < _MINIMAL_CONTENT_THRESHOLD:
                return (
                    f"Warning: page content appears minimal ({len(page_text)} chars) — "
                    f"this site may require JavaScript rendering and may not have loaded fully. "
                    f"Extracted content: {page_text!r}"
                )

            return self._extract_from_text(page_text, parameters_to_extract)

        except HTTPError as e:
            return f"Could not reach the provided URL (HTTP {e.response.status_code}): {url}"
        except requests.exceptions.ConnectionError:
            return f"Connection error — could not reach: {url}"
        except requests.exceptions.Timeout:
            return f"Request timed out after 15 seconds: {url}"
        except Exception as e:
            logger.error("Unexpected error fetching %s: %s", url, e)
            return "Internal error — could not fetch or extract data from the page."

    def _extract_from_text(self, page_text: str, parameters_to_extract: str) -> str:
        prompt = ChatPromptTemplate.from_messages([("system", EXTRACT_DATA_PROMPT)])
        messages = prompt.format_messages(input=page_text, keys=parameters_to_extract)
        return self._llm.invoke(messages).content

    def _get_proxies(self) -> dict | None:
        if self.CONFIGURATION_ARGS.proxy:
            return {
                "http": self.CONFIGURATION_ARGS.proxy,
                "https": self.CONFIGURATION_ARGS.proxy,
            }
        return None
