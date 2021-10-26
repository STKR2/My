from pyrogram import Client
from pytgcalls import PyTgCalls
from config import SESSION_NAME, API_ID, API_HASH, BOT_TOKEN

bot = Client(
  ":memory:",
  API_ID,
  API_HASH,
  bot_token=BOT_TOKEN,
  plugins=dict(root="program")
)
user = Client(SESSION_NAME, API_ID, API_HASH)
call_py = PyTgCalls(user)
