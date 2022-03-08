"""
Video + Music Stream Telegram Bot
Copyright (c) 2022-present levina=lab <https://github.com/levina-lab>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but without any warranty; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/licenses.html>
"""


import os
import re
import uuid
import socket
import psutil
import platform

from config import BOT_USERNAME

from program import LOGS
from driver.core import me_bot
from driver.filters import command
from driver.utils import remove_if_exists
from driver.decorators import sudo_users_only, humanbytes

from pyrogram import Client, filters
from pyrogram.types import Message


@Client.on_message(command(["sysinfo", f"sysinfo@{BOT_USERNAME}"]) & ~filters.edited)
@sudo_users_only
async def fetch_system_information(client, message):
    splatform = platform.system()
    platform_release = platform.release()
    platform_version = platform.version()
    architecture = platform.machine()
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(socket.gethostname())
    mac_address = ":".join(re.findall("..", "%012x" % uuid.getnode()))
    processor = platform.processor()
    ram = humanbytes(round(psutil.virtual_memory().total))
    cpu_freq = psutil.cpu_freq().current
    if cpu_freq >= 1000:
        cpu_freq = f"{round(cpu_freq / 1000, 2)}GHz"
    else:
        cpu_freq = f"{round(cpu_freq, 2)}MHz"
    du = psutil.disk_usage(client.workdir)
    psutil.disk_io_counters()
    disk = f"{humanbytes(du.used)} / {humanbytes(du.total)} " f"({du.percent}%)"
    cpu_len = len(psutil.Process().cpu_affinity())
    somsg = f"""🖥 **System Information**
    
**PlatForm :** `{splatform}`
**PlatForm - Release :** `{platform_release}`
**PlatForm - Version :** `{platform_version}`
**Architecture :** `{architecture}`
**HostName :** `{hostname}`
**IP :** `{ip_address}`
**Mac :** `{mac_address}`
**Processor :** `{processor}`
**Ram : ** `{ram}`
**CPU :** `{cpu_len}`
**CPU FREQ :** `{cpu_freq}`
**DISK :** `{disk}`
    """
    
    await message.reply(somsg)


@Client.on_message(command(["logs", f"logs@{BOT_USERNAME}"]) & ~filters.edited)
@sudo_users_only
async def get_bot_logs(c: Client, m: Message):
    bot_log_path = f'streambot-logs-{me_bot.id}.txt'
    if os.path.exists(bot_log_path):
        try:
            await m.reply_document(
                bot_log_path,
                quote=True,
                caption='📁 this is the bot logs',
            )
        except Exception as e:
            remove_if_exists(bot_log_path)
            print(f'[ERROR]: {e}')
    else:
        if not os.path.exists(bot_log_path):
            await m.reply_text('❌ no logs found !')
