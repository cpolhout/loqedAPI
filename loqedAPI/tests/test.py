import asyncio
import aiohttp
import logging

from ..loqed import APIClient
from ..loqed import LoqedAPI
from ..loqed import Lock

logging.basicConfig(level=logging.DEBUG)

async def main():
    async with aiohttp.ClientSession() as session:
        #apiclient = APIClient(session, "https://bc615891-1f7d-4237-8b72-f20e5719d50e.mock.pstmn.io/api", "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiI5NGRiMDgyOS00ZWY4LTQ4ODEtYjY4YS05NGZkOTY1NWY0MzgiLCJqdGkiOiI1NDI5MzI2OTRlMmMxYzgxODk3YzU1YzE1YzZlOTMyYmE4MDdhYWFmNWEyNTQ4ZjhiMWExMTBlNjRkMzY4MmVjYzdhNmU2NTBlMWM5Yzc5NyIsImlhdCI6MTYzNzAyMDcxNy42NjM5NTcsIm5iZiI6MTYzNzAyMDcxNy42NjQyNDcsImV4cCI6MTY1MjY1OTExNS4yOTA4MDYsInN1YiI6IjEwNjEiLCJzY29wZXMiOltdfQ.B7eZUgQjDT6wOfJ6I0LnRa4_2eTEiKkCqrQzXu9dB_eC-ak4yPdxf0YvNhniLNwiS0AxdZq2P2aRlpxlo8g7SwECIz06SqiYHjc26LHraRUwJeXL2y_2beMcm7Xbi9tN_AfNZ0lSh_Sdj1WDDRSTDnsDp7JP2jMrIxVJBMJzhI_traRnTcs_5O41Mlgrg8372HyLWd64QrUDaVQB34tDX6wKpRCSUHeSLJX_DmPM-LUenslGEy_pva0OSQljjqG9LcZY7uC2bcaz6R7ZSDPq1qlsaRTshDZvpRfZ-bB1S0yw6wpTZ4Y2bhNbXHtZmejRLfiRn2JjHTisCQwxWaKYM-1EfemMXP5AZPstwOGTdB0vUBqsTtYHPpEEHgm94oznVlPRtjLu0uWYUXT07PFmZtDlXp6GD6gM1ZP376-nXL0kjimfhAntcSsxKGiJg7yw4hQt6oID50o3kk2_nbeIiCEIYMmeiSgGe2XNMo11SR_gn60jHGWJT6YrukkB5Ywqpnw_xqi2TQwIEydhJMqoHjJyTju_0vTlKh8LCXC064DIyU6QhMG5QOPMJ3xKgGdsg1rTHVh3vd39Y42SDQ3yj_CQHuvQsmjP-fSgJ-BVepJk4Ae5VdFTb49w7qNPg91pPCr0EGbHA54kGIeTdemsTLnj7A1MEjO64Sj9jO8V6FE")
        apiclient = APIClient(session, "https://integrations.production.loqed.com/api", "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiI5NGRiMDgyOS00ZWY4LTQ4ODEtYjY4YS05NGZkOTY1NWY0MzgiLCJqdGkiOiI1NDI5MzI2OTRlMmMxYzgxODk3YzU1YzE1YzZlOTMyYmE4MDdhYWFmNWEyNTQ4ZjhiMWExMTBlNjRkMzY4MmVjYzdhNmU2NTBlMWM5Yzc5NyIsImlhdCI6MTYzNzAyMDcxNy42NjM5NTcsIm5iZiI6MTYzNzAyMDcxNy42NjQyNDcsImV4cCI6MTY1MjY1OTExNS4yOTA4MDYsInN1YiI6IjEwNjEiLCJzY29wZXMiOltdfQ.B7eZUgQjDT6wOfJ6I0LnRa4_2eTEiKkCqrQzXu9dB_eC-ak4yPdxf0YvNhniLNwiS0AxdZq2P2aRlpxlo8g7SwECIz06SqiYHjc26LHraRUwJeXL2y_2beMcm7Xbi9tN_AfNZ0lSh_Sdj1WDDRSTDnsDp7JP2jMrIxVJBMJzhI_traRnTcs_5O41Mlgrg8372HyLWd64QrUDaVQB34tDX6wKpRCSUHeSLJX_DmPM-LUenslGEy_pva0OSQljjqG9LcZY7uC2bcaz6R7ZSDPq1qlsaRTshDZvpRfZ-bB1S0yw6wpTZ4Y2bhNbXHtZmejRLfiRn2JjHTisCQwxWaKYM-1EfemMXP5AZPstwOGTdB0vUBqsTtYHPpEEHgm94oznVlPRtjLu0uWYUXT07PFmZtDlXp6GD6gM1ZP376-nXL0kjimfhAntcSsxKGiJg7yw4hQt6oID50o3kk2_nbeIiCEIYMmeiSgGe2XNMo11SR_gn60jHGWJT6YrukkB5Ywqpnw_xqi2TQwIEydhJMqoHjJyTju_0vTlKh8LCXC064DIyU6QhMG5QOPMJ3xKgGdsg1rTHVh3vd39Y42SDQ3yj_CQHuvQsmjP-fSgJ-BVepJk4Ae5VdFTb49w7qNPg91pPCr0EGbHA54kGIeTdemsTLnj7A1MEjO64Sj9jO8V6FE")
        api = LoqedAPI(apiclient)

        locks = await api.async_get_locks()
        print(f"The lock name: {locks[0].name}")
        print(f"The lock ID: {locks[0].id}")

        print("Opening lock")

       # await locks[0].open()


asyncio.run(main())