from aiohttp import ClientSession
from .loqed import AbstractAPIClient
from .urls import CLOUD_BASE_URL


class CloudAPIClient(AbstractAPIClient):
    def __init__(self, websession: ClientSession, token: str | None = None):
        """Initialize the auth."""
        super().__init__(websession, CLOUD_BASE_URL, token)


class LoqedCloudAPI:
    def __init__(self, apiclient: CloudAPIClient):
        self.apiclient = apiclient

    async def async_get_locks(self):
        resp = await self.apiclient.request("get", "api/locks/")
        resp.raise_for_status()
        return await resp.json()
