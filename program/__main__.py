import os
from pyrogram import Client, idle
from pytgcalls import PyTgCalls
from pytgcalls import idle as engine
from driver.veez import bot, call_py
from program import __version__

await bot.start()
print(f"program v{__version__} started !")
await call_py.start()
print("program client started !")
await engine()
await idle()
