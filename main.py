import asyncio

from program import LOGS
from pytgcalls import idle
from driver.core import calls, bot, user, lang_


async def start_bot():
    await bot.start()
    LOGS.info(lang_.get("client_started"))
    await calls.start()
    LOGS.info(lang_.get("pytgcall_started"))
    await user.join_chat("VeezSupportGroup")
    await user.join_chat("levinachannel")
    await idle()
    LOGS.info(lang_.get("client_stopped"))
    await bot.stop()

loop = asyncio.get_event_loop_policy().get_event_loop()
loop.run_until_complete(start_bot())
