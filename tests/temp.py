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
        apiclient = APIClient(session, "http://10.0.0.104")
        api = LoqedAPI(apiclient)
        secret='VUoI/HmtiN7WYTnXkB/NdiGaICC60KFz9OxtnJ4ebHY='
        bridgekey='Go6L8l83Lf7oGMhaBCbDzwNTOUmfKPCS9uN0a1KfPz4='
        lock = await api.async_get_lock(secret,bridgekey, 2, "Polhuiss")
        print(f"The lock name: {lock.name}")
        print(f"The lock ID: {lock.id}")
        print(f"Locking the lock...")
        # await lock.unlock()

        print(f"Registering dummy hook..")
        json_data=await lock.getWebhooks()
        for hook in json_data:
            print("FOUND WEBHOOK:" + str(hook))

        # status=await lock.registerWebhook("https://webhook.site/162bed3b-445e-4571-8b44-4a3f132961a4")
        # print(status)

        json_data=await lock.getWebhooks()
        for hook in json_data:
            print("FOUND WEBHOOK:" + str(hook))



asyncio.run(main())