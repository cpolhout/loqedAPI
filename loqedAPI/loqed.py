"""
Loqed API integration
"""

import logging
import aiohttp
#from .apiclient import APIClient
from typing import List
import os
import json
from abc import abstractmethod
from asyncio import CancelledError, TimeoutError, get_event_loop
from aiohttp import ClientError, ClientSession, ClientResponse
from typing import List

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
log = logging.getLogger("trace")

class AbstractAPIClient():
    """Client to handle API calls."""

    def __init__(self, websession: ClientSession, host):
        """Initialize the client."""
        self.websession = websession
        self.host = host
        print("API CLIENT CREATED")

    @abstractmethod
    async def async_get_access_token(self) -> str:
        """Return a valid access token."""

    async def request(self, method, url, **kwargs) -> ClientResponse:
        """Make a request."""
        headers = kwargs.get("headers")

        if headers is None:
            headers = {}
        else:
            headers = dict(headers)

        access_token = await self.async_get_access_token()
        headers["authorization"] = f"Bearer {access_token}"

        return await self.websession.request(
            method, f"{self.host}/{url}", **kwargs, headers=headers,
        )


class APIClient(AbstractAPIClient):
    def __init__(self, websession: ClientSession, host: str, token: str):
        """Initialize the auth."""
        super().__init__(websession, host)
        self.token = token

    async def async_get_access_token(self) -> str:
        """Return a valid access token."""
        return self.token
        


class Lock:
    """Class that represents a Lock object in the LoqedAPI."""

    def __init__(self, raw_data: dict, apiclient: APIClient):
        """Initialize a lock object."""
        self.raw_data = raw_data
        self.apiclient = apiclient
    

    @property
    def id(self) -> str:
        """Return the ID of the lock."""
        return self.raw_data["id"]

    @property
    def name(self) -> str:
        """Return the name of the lock."""
        return self.raw_data["name"]
    
    @property
    def battery_percentage(self) -> int:
        """Return the name of the lock."""
        return self.raw_data["battery_percentage"]

    @property
    def battery_type(self) -> str:
        """Return the name of the lock."""
        return self.raw_data["battery_type"]

    @property
    def bolt_state(self) -> str:
        """Return the name of the lock."""
        return self.raw_data["bolt_state"]

    @property
    def party_mode(self) -> bool:
        """Return the name of the lock."""
        return self.raw_data["party_mode"]

    @property
    def guest_access_mode(self) -> bool:
        """Return the name of the lock."""
        return self.raw_data["guest_access_mode"]

    @property
    def twist_assist(self) -> bool:
        """Return the name of the lock."""
        return self.raw_data["twist_assist"]

    @property
    def touch_to_connect(self) -> bool:
        """Return the name of the lock."""
        return self.raw_data["touch_to_connect"]
    
    @property
    def lock_direction(self) -> str:
        """Return the name of the lock."""
        return self.raw_data["lock_direction"]
    
    @property
    def mortise_lock_type(self) -> str:
        """Return the name of the lock."""
        return self.raw_data["mortise_lock_type"]

    @property
    def supported_lock_states(self) -> str:
        """Return the name of the lock."""
        return self.raw_data["supported_lock_states"]

    async def open(self):
        "Open the lock"
        resp = await self.apiclient.request("get", f"locks/{self.id}/bolt_state/open")
        resp.raise_for_status()
        print("Response" + await resp.text())

    async def lock(self):
        "Set night-lock"
        resp = await self.apiclient.request("get", f"locks/{self.id}/bolt_state/night_lock")
        resp.raise_for_status()
        print("Response" + await resp.text())
    
    async def unlock(self):
        "Set day-lock"
        resp = await self.apiclient.request("get", f"locks/{self.id}/bolt_state/day_lock")
        resp.raise_for_status()
        print("Response" + await resp.text())
    
    async def update(self):
        "Update status"
        resp = await self.apiclient.request("get", "locks")
        resp.raise_for_status()
        json_data = await resp.json()
        for lock_data in json_data["data"]:
            if lock_data["id"]==self.raw_data["id"]:
                self.raw_data=lock_data
        print("Response UPDATED" + await resp.text())




class LoqedAPI:

    def __init__(self, apiclient: APIClient):
        """Initialize the API and store the auth so we can make requests."""
        self.apiclient = apiclient

    async def async_get_locks(self) -> List[Lock]:
        """Return the locks."""
        resp = await self.apiclient.request("get", "locks")
        print("Response" + await resp.text())
        json_data = await resp.json()
        return [Lock(lock_data, self.apiclient) for lock_data in json_data["data"]]
        resp.raise_for_status()


# NOT supported in API Yet
    # async def async_get_lock(self, lock_id) -> Lock:
    #     """Return a Lock."""
    #     resp = await self.apiclient.request("get", f"lock/{lock_id}")
    #     resp.raise_for_status()
    #     return Lock(await resp.json(), self.apiclient)



   
"""Loqed: Exceptions"""


class LoqedException(BaseException):
    """Raise this when something is off."""


class LoqedAuthenticationException(LoqedException):
    """Raise this when there is an authentication issue."""


    # def get_locks(self):
    #         """Return a list of kiwi locks."""
    #         self._with_valid_session()
    #         sensor_list = requests.get(
    #             API_LIST_DOOR_URL,
    #             params={"session_key": self.__session_key, "page_size": 999},
    #             headers={"Accept": "application/json"},
    #             timeout=self.__timeout
    #         )
    #         if not sensor_list.ok:
    #             _LOGGER.error("could not get your KIWI doors.")
    #             return []

    #         doors = sensor_list.json()['result']['sensors']
    #         return doors

    # def open_door(self, door_id):
    #     """Open the kiwi door lock."""
    #     self._with_valid_session()
    #     open_response = requests.post(
    #         API_OPEN_DOOR_URL.format(door_id),
    #         headers={"Accept": "application/json"},
    #         params={"session_key": self.__session_key},
    #         timeout=self.__timeout
    #     )
    #     if not open_response.ok:
    #         raise KiwiException(
    #             "Could not open door",
    #             {'status_code': open_response.status_code}