import logging

import requests
from bs4 import BeautifulSoup
from enthusiast_common.tools import BaseLLMTool
from enthusiast_common.utils import RequiredFieldsModel
from langchain_core.messages import HumanMessage, SystemMessage
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


class ScrapeProductInput(BaseModel):
    """Input schema for ScrapeProductTool."""

    url: str = Field(description="URL of the product web page to fetch and extract data from")
    action: str = Field(
        description=(
            "Describe what data to extract from the page and any additional context "
            "(e.g. which fields to look for, hints about where data is located on the page, "
            "or format requirements such as returning price as a plain decimal number)."
        )
    )


class ScrapeProductConfig(RequiredFieldsModel):
    """Runtime configuration for ScrapeProductTool."""

    proxy: str = Field(
        title="Proxy",
        description="Optional proxy address to use when fetching web pages (e.g. 'http://proxy:8080'). Leave empty to fetch directly.",
        default="",
    )


class ScrapeProductTool(BaseLLMTool):
    """Fetches a product web page and extracts structured product data from it using an LLM.

    Uses plain HTTP requests and BeautifulSoup for content extraction. JavaScript-rendered
    pages (SPAs) may return minimal content — in that case the tool returns a warning so the
    agent can relay it to the user.
    """

    NAME = "scrape_product_data"
    DESCRIPTION = (
        "Fetches a product web page from the given URL and extracts product data from its content. "
        "Provide the URL and a description of what data to extract and any format requirements. "
        "Does not support JavaScript-rendered pages — static HTML only."
    )
    ARGS_SCHEMA = ScrapeProductInput
    RETURN_DIRECT = False
    CONFIGURATION_ARGS = ScrapeProductConfig

    def run(self, url: str, action: str) -> str:
        """Fetch the page at `url` and extract the requested fields via LLM.

        Args:
            url: The product page URL to scrape.
            action: Free-form extraction instruction passed as context to the LLM sub-call.

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

            return self._extract_from_text(page_text, action)

        except HTTPError as e:
            return f"Could not reach the provided URL (HTTP {e.response.status_code}): {url}"
        except requests.exceptions.ConnectionError:
            return f"Connection error — could not reach: {url}"
        except requests.exceptions.Timeout:
            return f"Request timed out after 15 seconds: {url}"
        except Exception as e:
            logger.error("Unexpected error fetching %s: %s", url, e)
            return "Internal error — could not fetch or extract data from the page."

    def _extract_from_text(self, page_text: str, action: str) -> str:
        messages = [
            SystemMessage(content=action),
            HumanMessage(content=page_text),
        ]
        return self._llm.invoke(messages).content

    def _get_proxies(self) -> dict | None:
        if self.CONFIGURATION_ARGS.proxy:
            return {
                "http": self.CONFIGURATION_ARGS.proxy,
                "https": self.CONFIGURATION_ARGS.proxy,
            }
        return None
