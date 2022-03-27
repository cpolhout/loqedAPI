import asyncio
import aiohttp
import logging
import os
print('cwd is %s' %(os.getcwd()))

from loqedAPI.loqed import APIClient
from loqedAPI.loqed import LoqedAPI
from loqedAPI.loqed import Lock

logging.basicConfig(level=logging.DEBUG)

async def main():
    async with aiohttp.ClientSession() as session:
        #apiclient = APIClient(session, "https://bc615891-1f7d-4237-8b72-f20e5719d50e.mock.pstmn.io/api", "")
        apiclient = APIClient(session, "http://xxx")
        api = LoqedAPI(apiclient)
        secret='xxxx'
        bridgekey='xxxx'
        lock = await api.async_get_lock(secret,bridgekey,2, "xxxx")
        print(f"The lock name: {lock.name}")
        print(f"The lock ID: {lock.id}")
        print(f"Locking the lock...")
        # await lock.unlock()

        print(f"Registering dummy hook..")
        json_data=await lock.getWebhooks()
        for hook in json_data:
            print("FOUND WEBHOOK:" + str(hook))

        status=await lock.registerWebhook("https://webhook.site/xxx")
        print(status)

        json_data=await lock.getWebhooks()
        for hook in json_data:
            print("FOUND WEBHOOK:" + str(hook))



asyncio.run(main())