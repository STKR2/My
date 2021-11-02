import asyncio
from pytgcalls import idle
from driver.veez import call_py, bot, user

BOT_ID = 0
BOT_NAME = ""
BOT_USERNAME = ""
USERBOT_ID = 0
USERBOT_NAME = ""
USERBOT_USERNAME = ""
USERBOT_MENTION = ""

async def all_info(bot, user):
    global BOT_ID, BOT_NAME, BOT_USERNAME
    global USERBOT_ID, USERBOT_NAME, USERBOT_MENTION, USERBOT_USERNAME
    getme = await bot.get_me()
    getme1 = await user.get_me()
    BOT_ID = getme.id
    USERBOT_ID = getme1.id
    if getme.last_name:
        BOT_NAME = getme.first_name + " " + getme.last_name
    else:
        BOT_NAME = getme.first_name
    BOT_USERNAME = getme.username
    USERBOT_NAME = (
        f"{getme1.first_name} {getme1.last_name}"
        if getme1.last_name
        else getme1.first_name
    )
    USERBOT_USERNAME = getme1.username
    USERBOT_MENTION = getme1.mention


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
