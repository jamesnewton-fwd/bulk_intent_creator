import requests

from .exceptions import APIError
from .models import IntentCheck


class ForwardNetworksClient:
    """Thin wrapper around the Forward Networks REST API.

    Uses HTTP Basic auth with api_key as the username and an empty password.
    Adjust the auth tuple if your instance uses a different scheme.
    """

    def __init__(self, host: str, api_key: str, api_secret: str) -> None:
        self._base_url = host.rstrip("/") + "/api"
        self._session = requests.Session()
        self._session.auth = (api_key, api_secret)
        self._session.headers.update({"Content-Type": "application/json"})

    def add_check(self, check: IntentCheck, snapshot_id: str) -> dict:
        url = f"{self._base_url}/snapshots/{snapshot_id}/checks"
        response = self._session.post(url, json=check.to_api_payload())
        self._raise_for_status(response)
        return response.json()

    def _raise_for_status(self, response: requests.Response) -> None:
        if not response.ok:
            raise APIError(response.status_code, response.text)
