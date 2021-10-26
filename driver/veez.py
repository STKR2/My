from pyrogram import Client
from pytgcalls import PyTgCalls
from config import SESSION_NAME, API_ID, API_HASH

bot = Client(
  SESSION_NAME,
  API_ID,
  API_HASH,
  plugins=dict(root="program")
)

call_py = PyTgCalls(bot)
