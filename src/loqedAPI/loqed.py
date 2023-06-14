"""
Loqed API integration
This is the local API integration. For the remote integration look at LoqedAPI_internet
"""

from enum import Enum
import logging
from typing import List
import os
import json
from abc import abstractmethod
from asyncio import get_event_loop
from aiohttp import ClientSession, ClientResponse
from typing import List
import struct
import time
import hmac
import base64
import hashlib
import urllib

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
_LOGGER = logging.getLogger(__name__)

class Action(Enum):
    OPEN = 1
    UNLOCK = 2
    LOCK = 3

class AbstractAPIClient():
    """Client to handle API calls."""

    def __init__(self, websession: ClientSession, host: str, token: str | None = None):
        """Initialize the client."""
        self.websession = websession
        self.host = host
        self.token = token
        _LOGGER.debug("API client created")

    async def request(self, method, url, **kwargs) -> ClientResponse:
        """Make a request."""
        headers = kwargs.get("headers")

        if headers is None:
            headers = {}
        else:
            headers = dict(headers)

        if self.token:
            headers["authorization"] = f"Bearer {self.token}"

        return await self.websession.request(
            method, f"{self.host}/{url}", **kwargs, headers=headers,
        )

class APIClient(AbstractAPIClient):
    def __init__(self, websession: ClientSession, host: str, token: str | None = None):
        """Initialize the auth."""
        super().__init__(websession, host, token)


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
        self.last_key_id = ""
        self.waitforstate = False
        self.last_event = ""
        self.id = self.raw_data["bridge_mac_wifi"]
    
    @property
    def battery_voltage(self) -> str:
        """Return the ID of the lock."""
        return self.raw_data["battery_voltage"]

    @property
    def wifi_strength(self) -> str:
        """Return the ID of the lock."""
        return self.raw_data["wifi_strength"]

    @property
    def ble_strength(self) -> str:
        """Return the ID of the lock."""
        return self.raw_data["ble_strength"]

    @property
    def battery_type(self) -> str:
        """Return the name of the lock."""
        return self.raw_data["battery_type"]

    def getcommand(self, action:Action) -> str:
        """Creates a hashed command to send to the loqed lock"""
        messageId_bin = struct.pack("Q", 0)
        protocol_bin = struct.pack("B", 2)
        command_type_bin = struct.pack("B", 7)
        local_key_id_bin = struct.pack("B", self.key_id)
        device_id_bin = struct.pack("B", 1)
        action_bin =  struct.pack("B", action.value)
        now=int(time.time())
        timenow_bin=now.to_bytes(8, 'big', signed=False)
        local_generated_binary_hash = protocol_bin + command_type_bin + timenow_bin + local_key_id_bin + device_id_bin + action_bin
        hm=hmac.new(base64.b64decode(self.secret), local_generated_binary_hash,hashlib.sha256).digest()
        command = messageId_bin + protocol_bin + command_type_bin + timenow_bin + hm + local_key_id_bin + device_id_bin + action_bin
        return urllib.parse.quote(base64.b64encode(command).decode("ascii"))

    async def sendcommand(self, type: Action) -> ClientResponse:
        """Sends the hashed command to the loqed lock"""
        command=self.getcommand(type)
        resp = await self.apiclient.request("get", f"to_lock?command_signed_base64={command}")
        resp.raise_for_status()
        return resp

    async def open(self) -> ClientResponse:
        "Open the lock"        
        return await self.sendcommand(Action.OPEN)

    async def lock(self) -> ClientResponse:
        "Set night-lock"
        return await self.sendcommand(Action.LOCK)
    
    async def unlock(self) -> ClientResponse:
        "Set day-lock"
        return await self.sendcommand(Action.UNLOCK)
    
    async def update(self):
        "Update status"
        resp = await self.apiclient.request("get", "status")
        resp.raise_for_status()
        json_data = await resp.json(content_type='text/html')
        self.raw_data=json_data
        self.bolt_state=self.raw_data["bolt_state"]
        return json_data

    async def getWebhooks(self):
        "Get webhooks for this lock"
        now=int(time.time())
        hash=hashlib.sha256(now.to_bytes(8, 'big', signed=False)+base64.b64decode(self.bridgekey)).hexdigest()
        headers = {'TIMESTAMP': str(now), 'HASH': hash}
        resp = await self.apiclient.request("get", f"webhooks", headers=headers)
        resp.raise_for_status()
        json_data = await resp.json(content_type='text/html')
        _LOGGER.debug("get Webhooks Response: %s", str(json_data))
        self.webhooks={}
        return json_data

    async def registerWebhook(self, url: str, flags:int = 511) -> str:
        "Register webhook for this lock subscribed to all events, first checks if its not already there"
        webhooks=await self.getWebhooks()
        for hook in webhooks:
            if hook["url"]==url: return "EXISTS ALREADY"
        now=int(time.time())
        hash=hashlib.sha256(url.encode() + flags.to_bytes(4, 'big') + now.to_bytes(8, 'big', signed=False)+base64.b64decode(self.bridgekey)).hexdigest()
        headers = {'TIMESTAMP': str(now), 'HASH': hash}
        json = {
            "url" : url,
            "trigger_state_changed_open" : flags >> 0 & 1,
            "trigger_state_changed_latch" : flags >> 1 & 1,
            "trigger_state_changed_night_lock" : flags >> 2 & 1,
            "trigger_state_changed_unknown" : flags >> 3 & 1,
            "trigger_state_goto_open" : flags >> 4 & 1,
            "trigger_state_goto_latch" : flags >> 5 & 1,
            "trigger_state_goto_night_lock" : flags >> 6 & 1,
            "trigger_battery" : flags >> 7 & 1,
            "trigger_online_status" : flags >> 8 & 1
        }
        resp = await self.apiclient.request("post", "webhooks", json=json, headers=headers)
        resp.raise_for_status()
        _LOGGER.debug("Create webhook Response: %s", await resp.text())
        return "CREATED"
    
    async def deleteWebhook(self, id: int) -> None:
        "Delete webhook for this lock"
        now=int(time.time())
        hash=hashlib.sha256(id.to_bytes(8, 'big', signed=False) + now.to_bytes(8, 'big', signed=False)+base64.b64decode(self.bridgekey)).hexdigest()
        headers = {'TIMESTAMP': str(now), 'HASH': hash}
        resp = await self.apiclient.request("delete", f"webhooks/{id}", headers=headers)
        resp.raise_for_status()
        _LOGGER.debug("Delete webhook Response: %s", await resp.text())
    
    async def receiveWebhook(self, body, hash: str, timestamp: str):
        "Received webhook with hash. This method checks the hash."
        timestamp=int(timestamp)
        now=int(time.time())
        data = json.loads(body) if body else {}
        if data=={}:
            error={"error": "Received invalid data from LOQED. Data needs to be formatted as JSON", "body": body, "hash": hash, "timestamp": timestamp, "now": now}
            _LOGGER.error(
                "ERROR: %s",error                
            )
            return error

        if not isinstance(data, dict):
            error={"error": "Received invalid data from LOQED. Data needs to be a dictionary", "body": body, "hash": hash, "timestamp": timestamp, "now": now}
            _LOGGER.error(
                "ERROR: %s",error                
            )
            return error
        _LOGGER.debug(" Received timestamp: %s , current timestamp: %s", str(timestamp), str(now))
        # check timestamp within 10 seconds
        if (now-timestamp>10) or (timestamp-now>10):
            error={"error": "Timestamp incorrect, possible replaying", "body": body, "hash": hash, "timestamp": timestamp, "now": now}
            _LOGGER.error(
                "ERROR: %s",error                
            )
            return error
        chash=hashlib.sha256(body.encode() + timestamp.to_bytes(8, 'big', signed=False)+base64.b64decode(self.bridgekey)).hexdigest()
        _LOGGER.debug("Received hash: %s , calculated hash: %s", hash, chash)
        if chash!=hash:
            error={"error": "Hash incorrect", "body": body, "hash": hash, "calculated_hash": chash, "timestamp": timestamp, "now": now}
            _LOGGER.error(
                "ERROR: %s",error                
            )
            return error
        if "battery_percentage" in data:
            self.battery_percentage=data["battery_percentage"]
        elif "ble_strength" in data:
            self.raw_data["ble_strength"] = data["ble_strength"]
        else:
            self.last_event=data["event_type"].strip().lower()
            # BOLT STATE CHANGE
            if self.last_event.split("_")[0]=="state": 
                self.bolt_state=str.replace(self.last_event,"state_changed_","")
            else:
                # BOLT IS CHANGING TO A STATE
                if "night_lock" in self.last_event: self.bolt_state="locking"
                if "open" in self.last_event: self.bolt_state="opening"
                if "latch" in self.last_event: self.bolt_state="unlocking"
            self.last_key_id=data["key_local_id"]
        return data

    async def updateState(self, state):
        self.bolt_state=state

class LoqedAPI:

    def __init__(self, apiclient: APIClient):
        """Initialize the API and store the auth so we can make requests."""
        self.apiclient = apiclient
    
    async def async_get_lock_details(self):
        """Return lock_info"""
        resp = await self.apiclient.request("get", "status")
        resp.raise_for_status()
        _LOGGER.debug("Response get lock details: %s",await resp.text())
        json_data = await resp.json(content_type='text/html')
        return json_data

    async def async_get_lock(self, secret: str, bridgekey: str, key_id: int, name: str, json_data=None) -> Lock:
        """Return the locks with lock-data"""
        if not json_data:
            resp = await self.apiclient.request("get", "status")
            json_data = await resp.json(content_type='text/html')
        return Lock(json_data, secret, bridgekey,  key_id, name, self.apiclient)

class LoqedCloudAPI:
    def __init__(self, apiclient: APIClient):
        self.apiclient = apiclient

    async def async_get_locks(self):
        resp = await self.apiclient.request("get", "/api/locks/")
        resp.raise_for_status()
        return await resp.json()
   
"""Loqed: Exceptions"""


class LoqedException(BaseException):
    """Raise this when something is off."""


class LoqedAuthenticationException(LoqedException):
    """Raise this when there is an authentication issue."""


