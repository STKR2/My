# Copyright (C) 2021 Veez Music-Project

from config import Config
from pyrogram import Client
from pytgcalls import PyTgCalls

VGA = Client(
    Config.SESSION,
    Config.API_ID,
    Config.API_HASH,
    plugins=dict(root="system")
    )

call_py = PyTgCalls(VGA, cache_duration=180)

############
#   inti   #
############

bot = Client(
    ":memory:",
    Config.API_ID,
    Config.API_HASH,
    bot_token=Config.BOT_TOKEN,
    plugins=dict(root="program")
)
