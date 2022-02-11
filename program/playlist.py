# Copyright (C) 2021 By Veez Music-Project
# Commit Start Date 20/10/2021
# Finished On 28/10/2021

from config import BOT_USERNAME
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
from pyrogram import Client, filters
from driver.queues import QUEUE, get_queue
from driver.filters import command, other_filters
from driver.database.dbpunish import is_gbanned_user


keyboard = InlineKeyboardMarkup(
    [[InlineKeyboardButton("🗑 Close", callback_data="set_close")]]
)


@Client.on_message(command(["playlist", f"playlist@{BOT_USERNAME}", "queue", f"queue@{BOT_USERNAME}"]) & other_filters)
async def playlist(client, m: Message):
    chat_id = m.chat.id
    user_id = m.from_user.id
    if await is_gbanned_user(user_id):
        await m.reply_text("❗️ **You've blocked from using this bot!**")
        return
    if chat_id in QUEUE:
        chat_queue = get_queue(chat_id)
        if len(chat_queue)==1:
            await m.reply(f"💡 **Currently Streaming**`:`\n\n*️⃣ [{chat_queue[0][0]}]({chat_queue[0][2]}) | `{chat_queue[0][3]}`", reply_markup=keyboard, disable_web_page_preview=True)
        else:
            QUE = f"💡 **Currently Streaming**`:`\n\n*️⃣ [{chat_queue[0][0]}]({chat_queue[0][2]}) | `{chat_queue[0][3]}` \n\n**📖 Queue song list**`:`\n"
            l = len(chat_queue)
            for x in range (1, l):
                han = chat_queue[x][0]
                hok = chat_queue[x][2]
                hap = chat_queue[x][3]
                QUE = QUE + "\n" + f"`#{x}` - [{han}]({hok}) | `{hap}`"
            await m.reply(QUE, reply_markup=keyboard, disable_web_page_preview=True)
    else:
        await m.reply("❌ **nothing is currently streaming.**")
