from requests import get
from pyrogram import Client
from pytgcalls import PyTgCalls
from config import API_HASH, API_ID, BOT_TOKEN, SESSION_NAME


bot = Client(
    ":veez:",
    API_ID,
    API_HASH,
    bot_token=BOT_TOKEN,
    plugins={"root": "program"},
)
# A bad way to do it, but it works
me = get(f"https://api.telegram.org/bot{BOT_TOKEN}/getme").json()["result"]
user = Client(
    SESSION_NAME,
    api_id=API_ID,
    api_hash=API_HASH,
)

calls = PyTgCalls(user, overload_quiet_mode=True)
