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


from pyrogram.types import Message
from pyrogram import Client, filters

from config import BOT_USERNAME
from driver.core import bot
from driver.filters import command
from driver.decorators import sudo_users_only
from driver.database.dblockchat import (
  blacklist_chat,
  blacklisted_chats,
  whitelist_chat,
)


@Client.on_message(command(["block", f"block@{BOT_USERNAME}", "blacklist"]) & ~filters.edited)
@sudo_users_only
async def blacklist_chat_func(_, message: Message):
    if len(message.command) != 2:
        return await message.reply_text(
            "**usage:**\n\n» /block (`chat_id`)"
        )
    chat_id = int(message.text.strip().split()[1])
    if chat_id in await blacklisted_chats():
        return await message.reply_text("This chat already blacklisted.")
    blacklisted = await blacklist_chat(chat_id)
    if blacklisted:
        return await message.reply_text(
            "✅ This chat has blacklisted!"
        )
    await message.reply_text("❗️ something wrong happened, check logs!")


@Client.on_message(command(["unblock", f"unblock@{BOT_USERNAME}", "whitelist"]) & ~filters.edited)
@sudo_users_only
async def whitelist_chat_func(_, message: Message):
    if len(message.command) != 2:
        return await message.reply_text(
            "**usage:**\n\n» /unblock (`chat_id`)"
        )
    chat_id = int(message.text.strip().split()[1])
    if chat_id not in await blacklisted_chats():
        return await message.reply_text("This chat already whitelisted.")
    whitelisted = await whitelist_chat(chat_id)
    if whitelisted:
        return await message.reply_text(
            "✅ This chat has whitelisted!"
        )
    await message.reply_text("❗️ something wrong happened, check logs!")


@Client.on_message(command(["blocklist", f"blocklist@{BOT_USERNAME}", "blacklisted"]) & ~filters.edited)
@sudo_users_only
async def blacklisted_chats_func(_, message: Message):
    text = "📵 » Blocked Chat list:\n\n"
    j = 0
    for count, chat_id in enumerate(await blacklisted_chats(), 1):
        try:
            title = (await bot.get_chat(chat_id)).title
        except Exception:
            title = "Private"
        j = 1
        text += f"**{count}. {title}** [`{chat_id}`]\n"
    if j == 0:
        await message.reply_text("❌ no blacklisted chat.")
    else:
        await message.reply_text(text)
