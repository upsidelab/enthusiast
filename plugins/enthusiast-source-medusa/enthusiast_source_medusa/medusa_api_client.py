import base64
from typing import Any

import requests


class MedusaAPIClient:
    def __init__(self, base_url: str, api_key: str):
        self._base_url = base_url
        self._headers = self._build_headers(api_key)

    def get(self, path: str, body: dict[str, Any] = None, params: dict[str, Any] = None) -> dict[str, Any]:
        url = f"{self._base_url}{path}"
        response = requests.get(url, data=body, headers=self._headers, params=params)
        response.raise_for_status()
        return response.json()

    def post(self, path: str, body: dict[str, Any] = None) -> dict[str, Any]:
        url = f"{self._base_url}{path}"
        response = requests.post(url, data=body, headers=self._headers)
        response.raise_for_status()
        return response.json()

    def _build_headers(self, api_key: str) -> dict[str, str]:
        encoded_api_key_bytes = base64.b64encode(api_key.encode("utf-8"))
        encoded_api_key = encoded_api_key_bytes.decode("utf-8")
        return {
            "Content-Type": "application/json",
            "Authorization": f"Basic {encoded_api_key}",
        }
