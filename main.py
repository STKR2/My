import asyncio

from program import BOT_ID, USERBOT_ID
from driver.veez import call_py, bot, user
from pytgcalls import idle


async def all_info(bot, user):
    global BOT_ID, USERBOT_ID
    getme = await bot.get_me()
    getme1 = await user.get_me()
    BOT_ID = getme.id
    USERBOT_ID = getme1.id


async def mulai_bot():
    print("[INFO]: STARTING BOT CLIENT")
    await bot.start()
    print("[INFO]: STARTING PYTGCALLS CLIENT")
    await call_py.start()
    print("[INFO]: GENERATING CLIENT PROFILE")
    await all_info(bot, user)
    await idle()
    print("[INFO]: STOPPING BOT")
    await bot.stop()


loop = asyncio.get_event_loop()
loop.run_until_complete(mulai_bot())
