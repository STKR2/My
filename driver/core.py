import asyncio
from pyrogram import Client
from pyrogram.types import User
from pytgcalls import PyTgCalls
from config import API_HASH, API_ID, BOT_TOKEN, SESSION_NAME


bot = Client(
    ":veez:",
    API_ID,
    API_HASH,
    bot_token=BOT_TOKEN
)

user = Client(
    SESSION_NAME,
    api_id=API_ID,
    api_hash=API_HASH,
)

calls = PyTgCalls(user, overload_quiet_mode=True)

with bot as app:
    me_bot = app.get_me()
with user as app:
    me_user = app.get_me()

bot = Client(  # type: ignore
    ":veez:",
    API_ID,
    API_HASH,
    bot_token=BOT_TOKEN,
    plugins={"root": "program"},
)
