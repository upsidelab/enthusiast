import base64
from typing import Any

import requests

from enthusiast_common.errors import ECommerceConnectorError


class MedusaAPIClient:
    def __init__(self, base_url: str, api_key: str):
        self._base_url = base_url
        self._headers = self._build_headers(api_key)

    def get(self, path: str, body: dict[str, Any] = None, params: dict[str, Any] = None) -> dict[str, Any]:
        return self._request("GET", path, json=body, params=params)

    def post(self, path: str, body: dict[str, Any] = None) -> dict[str, Any]:
        return self._request("POST", path, json=body)

    def _request(self, method: str, path: str, **kwargs) -> dict[str, Any]:
        """Execute an HTTP request and raise ECommerceConnectorError for any failure."""
        url = f"{self._base_url}{path}"
        try:
            response = requests.request(method, url, headers=self._headers, **kwargs)
        except requests.exceptions.ConnectionError:
            raise ECommerceConnectorError(
                f"Could not connect to the Medusa API at {url}. "
                "Please check if the service is running and the base URL is configured correctly."
            )
        except requests.exceptions.Timeout:
            raise ECommerceConnectorError(f"Request to the Medusa API timed out at {url}.")
        except requests.exceptions.RequestException as e:
            # Walk the exception chain to find the root cause.
            # requests wraps low-level errors (e.g. OSError, socket errors) in its own exception types,
            # so str(e) would give a vague wrapper message. __cause__ is set by explicit "raise X from Y"
            # chaining, __context__ is set implicitly when an exception is raised inside an except block.
            # The loop traverses both until it reaches the original error with no further cause.
            root_cause = e
            while root_cause.__cause__ is not None or root_cause.__context__ is not None:
                root_cause = root_cause.__cause__ or root_cause.__context__
            raise ECommerceConnectorError(f"Medusa API request failed: {root_cause}")
        if not response.ok:
            # response.json() can fail if the body is not valid JSON (e.g. HTML error page, empty body),
            # so the except falls back to response.text to always produce a meaningful error message.
            try:
                message = response.json().get("message") or response.text
            except Exception:
                message = response.text
            raise ECommerceConnectorError(message, status_code=response.status_code)
        return response.json()

    def _build_headers(self, api_key: str) -> dict[str, str]:
        encoded_api_key_bytes = base64.b64encode(api_key.encode("utf-8"))
        encoded_api_key = encoded_api_key_bytes.decode("utf-8")
        return {
            "Content-Type": "application/json",
            "Authorization": f"Basic {encoded_api_key}",
        }
