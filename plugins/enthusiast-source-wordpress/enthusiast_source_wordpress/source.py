import logging
from typing import Optional

import re
import requests
import urllib.parse
from enthusiast_common import DocumentSourcePlugin, DocumentDetails
from requests import Response

logger = logging.getLogger(__name__)

class WordpressDocumentSource(DocumentSourcePlugin):
    def __init__(self, data_set_id, config: dict):
        """
        Initialize the plugin with the parameters to access shop.

        Args:
            data_set_id (int): identifier of a data set that documents are assigned to.
            config (dict): configuration of the plugin
        """
        super().__init__(data_set_id, config)

        self._wordpress_url = config.get("base_url")
        self._user_agent = config.get("user_agent", None)

    def fetch(self) -> list[DocumentDetails]:
        session = self._create_http_session()
        results = []

        current_url = self._posts_url()
        while current_url:
            logger.info(f"Fetching {current_url}")
            response = session.get(current_url)
            posts = response.json()
            results.extend([
                DocumentDetails(
                    url=post['link'],
                    title=post['title']['rendered'],
                    content=post['content']['rendered']
                )
                for post in posts
            ])
            current_url = self._next_page_link_from_headers(response)
        return results

    def _next_page_link_from_headers(self, response: Response) -> Optional[str]:
        link_header = response.headers['Link']

        match = re.search(r'<(\S+?)>; rel="next"', link_header)
        if match:
            return match.group(1)
        return None

    def _posts_url(self):
        return urllib.parse.urljoin(self._wordpress_url, 'wp-json/wp/v2/posts')

    def _create_http_session(self):
        session = requests.Session()
        if self._user_agent:
            session.headers.update({'User-Agent': self._user_agent})
        return session
