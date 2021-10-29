import asyncio

from driver.veez import bot, call_py
from pytgcalls import idle


async def mulai_bot():
    print("[INFO]: STARTING BOT CLIENT")
    await bot.start()
    print("[INFO]: STARTING PYTGCALLS CLIENT")
    await call_py.start()
    await idle()
    print("[INFO]: STOPPING BOT")
    await bot.stop()


loop = asyncio.get_event_loop()
loop.run_until_complete(mulai_bot())
