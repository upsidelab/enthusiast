import logging
import re
import urllib.parse

import requests
from enthusiast_common import DocumentDetails, DocumentSourcePlugin
from enthusiast_common.utils import RequiredFieldsModel
from pydantic import Field
from requests import Response

logger = logging.getLogger(__name__)


class WordpressConfig(RequiredFieldsModel):
    base_url: str = Field(title="Base URL", description="Base URL of the WordPress site")
    user_agent: str = Field(title="User agent", default="", description="Custom User-Agent for requests")


class WordpressDocumentSource(DocumentSourcePlugin):
    NAME = "WordPress"
    CONFIGURATION_ARGS = WordpressConfig

    def __init__(self, data_set_id, **kwargs):
        super().__init__(data_set_id)

    def fetch(self) -> list[DocumentDetails]:
        session = self._create_http_session()
        results = []

        current_url = self._posts_url()
        while current_url:
            logger.info(f"Fetching {current_url}")
            response = session.get(current_url)
            posts = response.json()
            results.extend(
                [
                    DocumentDetails(
                        url=post["link"], title=post["title"]["rendered"], content=post["content"]["rendered"]
                    )
                    for post in posts
                ]
            )
            current_url = self._next_page_link_from_headers(response)
        return results

    def _next_page_link_from_headers(self, response: Response) -> str:
        link_header = response.headers["Link"]

        match = re.search(r'<(\S+?)>; rel="next"', link_header)
        if match:
            return match.group(1)
        return ""

    def _posts_url(self):
        return urllib.parse.urljoin(self.CONFIGURATION_ARGS.base_url, "wp-json/wp/v2/posts")

    def _create_http_session(self):
        session = requests.Session()
        if self.CONFIGURATION_ARGS.user_agent:
            session.headers.update({"User-Agent": self.CONFIGURATION_ARGS.user_agent})
        return session
