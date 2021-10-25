from pytgcalls import PyTgCalls
from pyrogram import Client, filters
from config import SESSION_NAME, API_ID, API_HASH

contact_filter = filters.create(
    lambda _, __, message:
    (message.from_user and message.from_user.is_contact) or message.outgoing
)

bot = Client(
  SESSION_NAME,
  API_ID,
  API_HASH,
  plugins=dict(root="program")
)
call_py = PyTgCalls(bot)
