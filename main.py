import os
import asyncio
import logging
from pytgcalls import idle
from pyrogram import idle as pidle
from driver.veez import call_py, bot

if os.path.exists('log.txt'):
    with open('log.txt', 'r+') as f:
        f.truncate(0)

logging.basicConfig(
    format='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
    datefmt="[%X]",
    handlers=[
        logging.FileHandler('log.txt'),
        logging.StreamHandler()],
    level=logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.WARNING)

LOGGER = logging.getLogger(__name__)


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


LOGGER.info("✅ bot has been started")
