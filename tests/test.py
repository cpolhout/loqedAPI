import asyncio
import aiohttp
import logging

from loqedAPI import APIClient
from loqedAPI import LoqedAPI
from loqedAPI import Lock

logging.basicConfig(level=logging.DEBUG)

async def main():
    async with aiohttp.ClientSession() as session:
        #apiclient = APIClient(session, "https://bc615891-1f7d-4237-8b72-f20e5719d50e.mock.pstmn.io/api", "")
        apiclient = APIClient(session, "https://integrations.production.loqed.com/api", "xxx")
        api = LoqedAPI(apiclient)
        locks = await api.async_get_locks()
        print(f"The lock name: {locks[0].name}")
        print(f"The lock ID: {locks[0].id}")
        print(f"Registering dummy hook..")
        locks[0].registerWebhook("https://www.polhout.me/webhook/1212312121")

        print("Opening lock")

       # await locks[0].open()


asyncio.run(main())