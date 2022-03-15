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


import asyncio

from pyrogram import Client
from pyrogram.types import Message
from pyrogram.errors import FloodWait

from driver.core import me_bot
from driver.filters import command, other_filters
from driver.decorators import bot_creator
from driver.database.dbchat import get_served_chats
from driver.database.dbpunish import add_gban_user, is_gbanned_user, remove_gban_user

from config import OWNER_ID, SUDO_USERS, BOT_USERNAME as bn
from driver.utils import R


@Client.on_message(command(["gban", f"gban@{bn}"]) & other_filters)
@bot_creator
async def global_banned(c: Client, message: Message):
    BOT_NAME = me_bot.first_name
    if not message.reply_to_message:
        if len(message.command) < 2:
            await message.reply_text(R("gban_help"))
            return
        user = message.text.split(None, 2)[1]
        if "@" in user:
            user = user.replace("@", "")
        user = await c.get_users(user)
        from_user = message.from_user
        BOT_ID = me_bot.id
        if user.id == from_user.id:
            await message.reply_text(R("gban_self"))
        elif user.id == BOT_ID:
            await message.reply_text(R("gban_myself"))
        elif user.id in SUDO_USERS:
            await message.reply_text(R("gban_sudo"))
        elif user.id in OWNER_ID:
            await message.reply_text(R("gban_owner"))
        else:
            await add_gban_user(user.id)
            served_chats = []
            chats = await get_served_chats()
            for chat in chats:
                served_chats.append(int(chat["chat_id"]))
            m = await message.reply_text(R("gban_msg").format(user.mention, len(served_chats)))
            number_of_chats = 0
            for num in served_chats:
                try:
                    await c.ban_chat_member(num, user.id)
                    number_of_chats += 1
                    await asyncio.sleep(1)
                except FloodWait as e:
                    await asyncio.sleep(int(e.x))
                except Exception:
                    pass
            ban_text = R("gban_text").format(BOT_NAME, bn, message.chat.title, message.chat.id,
                                             from_user.mention, user.mention, user.id, number_of_chats)
            try:
                await m.delete()
            except Exception:
                pass
            await message.reply_text(ban_text, disable_web_page_preview=True,)
        return
    from_user_id = message.from_user.id
    from_user_mention = message.from_user.mention
    user_id = message.reply_to_message.from_user.id
    mention = message.reply_to_message.from_user.mention
    BOT_ID = me_bot.id
    if user_id == from_user_id:
        await message.reply_text(R("gban_self"))
    elif user_id == BOT_ID:
        await message.reply_text(R("gban_myself"))
    elif user_id in SUDO_USERS:
        await message.reply_text(R("gban_sudo"))
    elif user_id in OWNER_ID:
        await message.reply_text(R("gban_owner"))
    else:
        is_gbanned = await is_gbanned_user(user_id)
        if is_gbanned:
            await message.reply_text(R("gban_already"))
        else:
            await add_gban_user(user_id)
            served_chats = []
            chats = await get_served_chats()
            for chat in chats:
                served_chats.append(int(chat["chat_id"]))
            m = await message.reply_text(R("gban_msg").format(mention, len(served_chats)))
            number_of_chats = 0
            for num in served_chats:
                try:
                    await c.ban_chat_member(num, user_id)
                    number_of_chats += 1
                    await asyncio.sleep(1)
                except FloodWait as e:
                    await asyncio.sleep(int(e.x))
                except Exception:
                    pass
            ban_text = R("gban_text").format(BOT_NAME, bn, message.chat.title, message.chat.id,
                                             from_user_mention, mention, user_id, number_of_chats)
            try:
                await m.delete()
            except Exception:
                pass
            await message.reply_text(ban_text, disable_web_page_preview=True,)
            return


@Client.on_message(command(["ungban", f"ungban@{bn}"]) & other_filters)
@bot_creator
async def ungban_global(c: Client, message: Message):
    chat_id = message.chat.id
    if not message.reply_to_message:
        if len(message.command) != 2:
            await message.reply_text(R("un_gban_help"))
            return
        user = message.text.split(None, 1)[1]
        if "@" in user:
            user = user.replace("@", "")
        user = await c.get_users(user)
        from_user = message.from_user
        BOT_ID = me_bot.id
        if user.id == from_user.id:
            await message.reply_text(R("un_gban_self"))
        elif user.id == BOT_ID:
            await message.reply_text(R("un_gban_myself"))
        elif user.id in SUDO_USERS:
            await message.reply_text(R("un_gban_sudo"))
        elif user.id in OWNER_ID:
            await message.reply_text(R("un_gban_owner"))
        else:
            is_gbanned = await is_gbanned_user(user.id)
            if not is_gbanned:
                await message.reply_text(R("un_gban_no"))
            else:
                msg = await message.reply_text(f"» {R('un_gban_process')}")
                await remove_gban_user(user.id)
                served_chats = []
                chats = await get_served_chats()
                for chat in chats:
                    served_chats.append(int(chat["chat_id"]))
                number_of_chats = 0
                for num in served_chats:
                    try:
                        await c.unban_chat_member(num, user.id)
                        number_of_chats += 1
                        await asyncio.sleep(1)
                    except FloodWait as e:
                        await asyncio.sleep(int(e.x))
                    except BaseException:
                        pass
                await msg.edit_text(f"✅ {R('un_gban')}")
        return
    from_user_id = message.from_user.id
    user_id = message.reply_to_message.from_user.id
    mention = message.reply_to_message.from_user.mention
    BOT_ID = me_bot.id
    if user_id == from_user_id:
        await message.reply_text(R("un_gban_self"))
    elif user_id == BOT_ID:
        await message.reply_text(R("un_gban_myself"))
    elif user_id in SUDO_USERS:
        await message.reply_text(R("un_gban_sudo"))
    elif user_id in OWNER_ID:
        await message.reply_text(R("un_gban_owner"))
    else:
        is_gbanned = await is_gbanned_user(user_id)
        if not is_gbanned:
            await message.reply_text(R("un_gban_no"))
        else:
            msg = await message.reply_text(f"» {R('un_gban_process')}")
            await remove_gban_user(user_id)
            served_chats = []
            chats = await get_served_chats()
            for chat in chats:
                served_chats.append(int(chat["chat_id"]))
            number_of_chats = 0
            for num in served_chats:
                try:
                    await c.unban_chat_member(num, user_id)
                    number_of_chats += 1
                    await asyncio.sleep(1)
                except FloodWait as e:
                    await asyncio.sleep(int(e.x))
                except BaseException:
                    pass
                await msg.edit_text(f"✅ {R('un_gban')}")
