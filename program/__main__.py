import os
from pyrogram import Client, idle
from pytgcalls import PyTgCalls
from pytgcalls import idle as engine
from driver.veez import bot, call_py
from program import __version__

bot.start()
print(f"program v{__version__} started !")
call_py.start()
print("program client started !")
engine()
idle()
