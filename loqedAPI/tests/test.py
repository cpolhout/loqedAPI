import asyncio
import aiohttp
import logging

from ..loqed import APIClient
from ..loqed import LoqedAPI
from ..loqed import Lock

logging.basicConfig(level=logging.DEBUG)

async def main():
    async with aiohttp.ClientSession() as session:
        #apiclient = APIClient(session, "https://bc615891-1f7d-4237-8b72-f20e5719d50e.mock.pstmn.io/api", "")
        apiclient = APIClient(session, "https://integrations.production.loqed.com/api", "xxx")
        api = LoqedAPI(apiclient)
        locks = await api.async_get_locks()
        print(f"The lock name: {locks[0].name}")
        print(f"The lock ID: {locks[0].id}")

        print("Opening lock")

       # await locks[0].open()


asyncio.run(main())