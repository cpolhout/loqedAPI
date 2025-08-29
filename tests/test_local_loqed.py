import pytest
from loqedAPI.local_loqed import Lock, APIClient, LoqedAPI
from loqedAPI.exceptions import LoqedException, LoqedAuthenticationException

class DummyAPIClient(APIClient):
    def __init__(self):
        pass
    async def request(self, method, url, **kwargs):
        class DummyResponse:
            async def json(self):
                return {"data": [{"id": "lock1", "name": "Front Door", "bolt_state": "locked", "battery_percentage": 80, "battery_type": "AA", "party_mode": False, "guest_access_mode": False, "twist_assist": True, "touch_to_connect": True, "lock_direction": "left", "mortise_lock_type": "euro", "supported_lock_states": "locked"}]}
            async def text(self):
                return "OK"
            def raise_for_status(self):
                pass
        return DummyResponse()

@pytest.mark.asyncio
async def test_lock_properties():
    raw_data = {
        "id": "lock1",
        "name": "Front Door",
        "bolt_state": "locked",
        "battery_percentage": 80,
        "battery_type": "AA",
        "party_mode": False,
        "guest_access_mode": False,
        "twist_assist": True,
        "touch_to_connect": True,
        "lock_direction": "left",
        "mortise_lock_type": "euro",
        "supported_lock_states": "locked"
    }
    lock = Lock(raw_data, DummyAPIClient())
    assert lock.id == "lock1"
    assert lock.name == "Front Door"
    assert lock.battery_percentage == 80
    assert lock.battery_type == "AA"
    assert lock.party_mode is False
    assert lock.guest_access_mode is False
    assert lock.twist_assist is True
    assert lock.touch_to_connect is True
    assert lock.lock_direction == "left"
    assert lock.mortise_lock_type == "euro"
    assert lock.supported_lock_states == "locked"

@pytest.mark.asyncio
async def test_loqedapi_get_locks():
    api = LoqedAPI(DummyAPIClient())
    locks = await api.async_get_locks()
    assert len(locks) == 1
    assert locks[0].name == "Front Door"
    assert locks[0].id == "lock1"

# Exception tests
def test_exceptions():
    with pytest.raises(LoqedException):
        raise LoqedException("Test exception")
    with pytest.raises(LoqedAuthenticationException):
        raise LoqedAuthenticationException("Auth exception")
