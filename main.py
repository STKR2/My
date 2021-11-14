import asyncio
from pytgcalls import idle
from driver.veez import call_py, bot

async def mulai_bot():
    print("[VEEZ]: STARTING BOT CLIENT")
    await bot.start()
    print("[VEEZ]: STARTING PYTGCALLS CLIENT")
    await call_py.start()
    await idle()
    await pidle()
    print("[VEEZ]: STOPPING BOT & USERBOT")
    await bot.stop()

loop = asyncio.get_event_loop()
loop.run_until_complete(mulai_bot())
