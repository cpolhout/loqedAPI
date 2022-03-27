"""
Loqed API integration
This is the local API integration. For the remote integration look at LoqedAPI_internet
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
import struct
import time
import hmac
import base64
import hashlib
import urllib

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
log = logging.getLogger("trace")

class AbstractAPIClient():
    """Client to handle API calls."""

    def __init__(self, websession: ClientSession, host):
        """Initialize the client."""
        self.websession = websession
        self.host = host
        print("API CLIENT CREATED")

    # @abstractmethod
    # async def async_get_access_token(self) -> str:
    #     """Return a valid access token."""

    async def request(self, method, url, **kwargs) -> ClientResponse:
        """Make a request."""
        # headers = kwargs.get("headers")

        # if headers is None:
        #     headers = {}
        # else:
        #     headers = dict(headers)

        # access_token = await self.async_get_access_token()
        # headers["authorization"] = f"Bearer {access_token}"

        return await self.websession.request(
            method, f"{self.host}/{url}", **kwargs,
        )


class APIClient(AbstractAPIClient):
    def __init__(self, websession: ClientSession, host: str):
        """Initialize the auth."""
        super().__init__(websession, host)

        


class Lock:
    """Class that represents a Lock object in the LoqedAPI."""

    def __init__(self, raw_data: dict, secret: str, bridgekey: str, key_id: int, name: str, apiclient: APIClient):
        """Initialize a lock object."""
        self.raw_data = raw_data
        self.secret = secret
        self.bridgekey = bridgekey
        self.key_id=key_id
        self.apiclient = apiclient
        self.webhooks = {}        
        self.name = name
        self.bolt_state= raw_data["bolt_state"]
        self.battery_percentage = raw_data["battery_percentage"]
    

    @property
    def id(self) -> str:
        """Return the ID of the lock."""
        return self.raw_data["bridge_mac_wifi"]
    
    # @property
    # def battery_percentage(self) -> int:
    #     """Return the name of the lock."""
    #     return self.battery_percentage

    @property
    def battery_type(self) -> str:
        """Return the name of the lock."""
        return self.raw_data["battery_type"]

    # @property
    # def bolt_state(self) -> str:
    #     """Return the state of the lock."""
    #     return self.bolt_state

    # @property
    # def party_mode(self) -> bool:
    #     """Return the name of the lock."""
    #     return self.raw_data["party_mode"]

    # @property
    # def guest_access_mode(self) -> bool:
    #     """Return the name of the lock."""
    #     return self.raw_data["guest_access_mode"]

    # @property
    # def twist_assist(self) -> bool:
    #     """Return the name of the lock."""
    #     return self.raw_data["twist_assist"]

    # @property
    # def touch_to_connect(self) -> bool:
    #     """Return the name of the lock."""
    #     return self.raw_data["touch_to_connect"]
    
    # @property
    # def lock_direction(self) -> str:
    #     """Return the name of the lock."""
    #     return self.raw_data["lock_direction"]
    
    # @property
    # def mortise_lock_type(self) -> str:
    #     """Return the name of the lock."""
    #     return self.raw_data["mortise_lock_type"]

    # @property
    # def supported_lock_states(self) -> str:
    #     """Return the name of the lock."""
    #     return self.raw_data["supported_lock_states"]

    def getcommand(self,action):
        messageId=0
        protocol = 2
        command_type = 7
        device_id = 1
        messageId_bin = struct.pack("Q", messageId)
        protocol_bin = struct.pack("B", protocol)
        command_type_bin = struct.pack("B", command_type)
        local_key_id_bin = struct.pack("B", self.key_id)
        device_id_bin = struct.pack("B", device_id)
        action_bin =  struct.pack("B", action)
        now=int(time.time())
        timenow_bin=now.to_bytes(8, 'big', signed=False)
        local_generated_binary_hash = protocol_bin + command_type_bin + timenow_bin + self.key_id + device_id_bin + action_bin
        hm=hmac.new(base64.b64decode(self.secret), local_generated_binary_hash,hashlib.sha256).digest()
        command = messageId_bin + protocol_bin + command_type_bin + timenow_bin + hm + self.key_id + device_id_bin + action_bin
        return urllib.parse.quote(base64.b64encode(command).decode("ascii"))


    async def open(self):
        "Open the lock"
        command=self.getcommand(1)
        resp = await self.apiclient.request("get", f"to_lock?command_signed_base64={command}")
        resp.raise_for_status()

    async def lock(self):
        "Set night-lock"
        command=self.getcommand(3)
        # print("COMMAND:" + str(command))
        resp = await self.apiclient.request("get", f"to_lock?command_signed_base64={command}")
        resp.raise_for_status()
    
    async def unlock(self):
        "Set day-lock"
        command=self.getcommand(2)
        resp = await self.apiclient.request("get", f"to_lock?command_signed_base64={command}")
        resp.raise_for_status()
    
    async def update(self):
        "Update status"
        resp = await self.apiclient.request("get", "locks")
        resp.raise_for_status()
        json_data = await resp.json()
        for lock_data in json_data["data"]:
            if lock_data["id"]==self.raw_data["id"]:
                self.raw_data=lock_data
                self.bolt_state=self.raw_data["bolt_state"]
        print("Response UPDATED" + await resp.text())

    async def getWebhooks(self):
        "Get webhooks for this lock"
        now=int(time.time())
        hash=hashlib.sha256(now.to_bytes(8, 'big', signed=False)+base64.b64decode(self.bridgekey)).hexdigest()
        headers = {'TIMESTAMP': str(now), 'HASH': hash}
        resp = await self.apiclient.request("get", f"webhooks", headers=headers)
        resp.raise_for_status()
        json_data = await resp.json(content_type='text/html')
        print("Response" + str(json_data))
        self.webhooks=json_data
        return json_data

    async def registerWebhook(self, url):
        "Register webhook for this lock subscribed to all events, first checks if its not already there"
        webhooks=await self.getWebhooks()
        for hook in webhooks:
            if hook["url"]==url: return "EXISTS ALREADY"
        now=int(time.time())
        hash=hashlib.sha256(url.encode() + (511).to_bytes(4, 'big') + now.to_bytes(8, 'big', signed=False)+base64.b64decode(self.bridgekey)).hexdigest()
        headers = {'TIMESTAMP': str(now), 'HASH': hash}
        json = {
            "url" : url,
            "trigger_state_changed_open" : 1,
            "trigger_state_changed_latch" : 1,
            "trigger_state_changed_night_lock" : 1,
            "trigger_state_changed_unknown" : 1,
            "trigger_state_goto_open" : 1,
            "trigger_state_goto_latch" : 1,
            "trigger_state_goto_night_lock" : 1,
            "trigger_battery" : 1,
            "trigger_online_status" : 1
        }
        resp = await self.apiclient.request("post", f"webhooks", json=json, headers=headers)
        resp.raise_for_status()
        print("Response" + await resp.text())
        return "CREATED"
    
    async def deleteWebhook(self, id):
        "Delete webhook for this lock"
        now=int(time.time())
        hash=hashlib.sha256(id.to_bytes(8, 'big', signed=False) + now.to_bytes(8, 'big', signed=False)+base64.b64decode(self.bridgekey)).hexdigest()
        headers = {'TIMESTAMP': str(now), 'HASH': hash}
        resp = await self.apiclient.request("delete", f"webhooks/" + id, headers=headers)
        resp.raise_for_status()
        print("Response" + await resp.text())
    
    async def receiveWebhook(self, data):
        if "battery_percentage" in data:
            self.battery_percentage=data["battery_percentage"]
        etype=data["event_type"]
        if etype.split("_")[1]=="state": 
            self.bolt_state=str.replace(etype,"trigger_state_","")


        


    async def updateState(self, state):
        self.bolt_state=state



class LoqedAPI:

    def __init__(self, apiclient: APIClient):
        """Initialize the API and store the auth so we can make requests."""
        self.apiclient = apiclient

    async def async_get_lock(self, secret, bridgekey, key_id, name) -> Lock:
        """Return the locks."""
        resp = await self.apiclient.request("get", "status")
        print("Response" + await resp.text())
        json_data = await resp.json(content_type='text/html')
        return Lock(json_data, secret, bridgekey,  key_id, name, self.apiclient)
        # return [Lock(lock_data, self.apiclient) for lock_data in json_data["data"]]


# NOT supported in API Yet§
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


