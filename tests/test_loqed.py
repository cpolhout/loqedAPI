import time
import base64
import hashlib
import pytest
from loqedAPI.loqed import Lock, LoqedAPI, APIClient

class DummyAPIClient(APIClient):
    def __init__(self):
        pass
    async def request(self, method, url, **kwargs):
        class DummyResponse:
            async def json(self, content_type=None):
                return {"bolt_state": "locked", "battery_percentage": 90, "battery_type": "AA", "bridge_mac_wifi": "lockid", "wifi_strength": "good", "ble_strength": "strong"}
            async def text(self):
                return "OK"
            def raise_for_status(self):
                pass
        return DummyResponse()

@pytest.mark.asyncio
async def test_lock_methods():
    raw_data = {"bolt_state": "locked", "battery_percentage": 90, "battery_type": "AA", "bridge_mac_wifi": "lockid", "wifi_strength": "good", "ble_strength": "strong"}
    valid_base64 = "U2VjcmV0U2VjcmV0U2VjcmV0U2VjcmV0U2VjcmV0U2VjcmU="
    lock = Lock(raw_data, valid_base64, valid_base64, 1, "TestLock", DummyAPIClient())
    assert lock.bolt_state == "locked"
    assert lock.battery_percentage == 90
    assert lock.battery_type == "AA"
    assert lock.id == "lockid"
    assert lock.wifi_strength == "good"
    assert lock.ble_strength == "strong"
    resp = await lock.open()
    assert await resp.text() == "OK"
    resp = await lock.lock()
    assert await resp.text() == "OK"
    resp = await lock.unlock()
    assert await resp.text() == "OK"

@pytest.mark.asyncio
async def test_loqedapi_get_lock():
    api = LoqedAPI(DummyAPIClient())
    valid_base64 = "U2VjcmV0U2VjcmV0U2VjcmV0U2VjcmV0U2VjcmV0U2VjcmU="
    lock = await api.async_get_lock(valid_base64, valid_base64, 1, "TestLock", {"bolt_state": "locked", "battery_percentage": 90, "battery_type": "AA", "bridge_mac_wifi": "lockid", "wifi_strength": "good", "ble_strength": "strong"})
    assert lock.name == "TestLock"
    assert lock.id == "lockid"
    assert lock.bolt_state == "locked"

@pytest.mark.asyncio
async def test_lock_receive_webhook_state_update():
    valid_base64 = "U2VjcmV0U2VjcmV0U2VjcmV0U2VjcmV0U2VjcmV0U2VjcmU="
    raw_data = {"bolt_state": "locked", "battery_percentage": 90, "battery_type": "AA", "bridge_mac_wifi": "lockid", "wifi_strength": "good", "ble_strength": "strong"}
    lock = Lock(raw_data, valid_base64, valid_base64, 1, "TestLock", DummyAPIClient())
    body = '{"battery_percentage": 80, "key_local_id": 1, "event_type": "STATE_CHANGED_NIGHT_LOCK"}'
    timestamp = str(int(time.time()))
    hash_val = hashlib.sha256(
        body.encode() + int(timestamp).to_bytes(8, "big", signed=False) + base64.b64decode(valid_base64)
    ).hexdigest() 
    await lock.receiveWebhook(body, hash_val, timestamp)
    assert lock.battery_percentage == 80

@pytest.mark.asyncio
async def test_lock_receive_webhook_invalid_hash():
    valid_base64 = "U2VjcmV0U2VjcmV0U2VjcmV0U2VjcmV0U2VjcmV0U2VjcmU="
    raw_data = {"bolt_state": "locked", "battery_percentage": 90, "battery_type": "AA", "bridge_mac_wifi": "lockid", "wifi_strength": "good", "ble_strength": "strong"}
    lock = Lock(raw_data, valid_base64, valid_base64, 1, "TestLock", DummyAPIClient())
    body = '{"battery_percentage": 80, "key_local_id": 1, "event_type": "STATE_CHANGED_NIGHT_LOCK"}'
    timestamp = str(int(time.time()))
    bad_hash = "deadbeef" * 8
    result = await lock.receiveWebhook(body, bad_hash, timestamp)
    assert "error" in result
    assert result["error"] == "Hash incorrect"

@pytest.mark.asyncio
async def test_lock_receive_webhook_invalid_timestamp():
    valid_base64 = "U2VjcmV0U2VjcmV0U2VjcmV0U2VjcmV0U2VjcmV0U2VjcmU="
    raw_data = {"bolt_state": "locked", "battery_percentage": 90, "battery_type": "AA", "bridge_mac_wifi": "lockid", "wifi_strength": "good", "ble_strength": "strong"}
    lock = Lock(raw_data, valid_base64, valid_base64, 1, "TestLock", DummyAPIClient())
    body = '{"battery_percentage": 80, "key_local_id": 1, "event_type": "STATE_CHANGED_NIGHT_LOCK"}'
    # Use a timestamp far in the past
    old_timestamp = str(int(time.time()) - 1000)
    hash_val = hashlib.sha256(
        body.encode() + int(old_timestamp).to_bytes(8, "big", signed=False) + base64.b64decode(valid_base64)
    ).hexdigest()
    result = await lock.receiveWebhook(body, hash_val, old_timestamp)
    assert "error" in result
    assert result["error"] == "Timestamp incorrect, possible replaying"