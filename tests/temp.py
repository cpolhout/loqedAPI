import asyncio
import aiohttp
import logging
import os
print('cwd is %s' %(os.getcwd()))

from loqedAPI.loqed import APIClient
from loqedAPI.loqed import LoqedAPI
from loqedAPI.loqed import Lock

logging.basicConfig(level=logging.DEBUG)

# 10.0.0.104|LOQED-c44f3357c161.local|Go6L8l83Lf7oGMhaBCbDzwNTOUmfKPCS9uN0a1KfPz4=|9|OABlBKkvNvCRBumNviMkZMDtY11/6s0GN4E6f8VkRY0=
# 10.0.0.104|LOQED-c44f3357c161.local|1wgT0FwrA5nxShOzWIyXdUCevFS0WBeZUBHCGsF4MeI=|9|Go6L8l83Lf7oGMhaBCbDzwNTOUmfKPCS9uN0a1KfPz4=

async def main():
    async with aiohttp.ClientSession() as session:
        #apiclient = APIClient(session, "https://bc615891-1f7d-4237-8b72-f20e5719d50e.mock.pstmn.io/api", "")
        apiclient = APIClient(session, "http://10.0.0.104")
        api = LoqedAPI(apiclient)
        secret='VUoI/HmtiN7WYTnXkB/NdiGaICC60KFz9OxtnJ4ebHY='
        bridgekey='Go6L8l83Lf7oGMhaBCbDzwNTOUmfKPCS9uN0a1KfPz4='
        lock = await api.async_get_lock(secret,bridgekey, 2, "Polhuiss")
        print(f"The lock name: {lock.name}")
        print(f"The lock ID: {lock.id}")
        print(f"Locking the lock...")
        await lock.lock()

        print(f"Registering dummy hook..")
        json_data=await lock.getWebhooks()
        for hook in json_data:
            print("FOUND WEBHOOK:" + str(hook))

        # status=await lock.registerWebhook("https://webhook.site/162bed3b-445e-4571-8b44-4a3f132961a4")
        # print(status)

        await lock.update()
        json_data=await lock.getWebhooks()
        for hook in json_data:
            print("FOUND WEBHOOK:" + str(hook))

        await lock.receiveWebhook('{"requested_state": "NIGHT_LOCK","requested_state_numeric": 3,"mac_wifi": "c44f3357c161","mac_ble": "c44f3357c163","event_type": "STATE_CHANGED_NIGHT_LOCK","key_local_id": 2}', 'eca8533245d05a97a02be3da8011f9832f67c19c1d2a519dc8a8814d98e84a8a', '1648673471')



asyncio.run(main())