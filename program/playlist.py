# Copyright (C) 2021 By Veez Music-Project
# Commit Start Date 20/10/2021
# Finished On 28/10/2021

from config import BOT_USERNAME
from pyrogram.types import Message
from driver.filters import command, other_filters
from pyrogram import Client, filters
from driver.queues import QUEUE, get_queue


@Client.on_message(command(["playlist", f"playlist@{BOT_USERNAME}", "queue", f"queue@{BOT_USERNAME}"]) & other_filters)
async def playlist(client, m: Message):
   chat_id = m.chat.id
   if chat_id in QUEUE:
      chat_queue = get_queue(chat_id)
      if len(chat_queue)==1:
         await m.reply(f"💡 **now playing:**\n\n[{chat_queue[0][0]}]({chat_queue[0][2]}) | `{chat_queue[0][3]}`", disable_web_page_preview=True)
      else:
         QUE = f"💡 **now playing:**\n\n[{chat_queue[0][0]}]({chat_queue[0][2]}) | `{chat_queue[0][3]}` \n\n**📖 play-list:**"
         l = len(chat_queue)
         for x in range (1, l):
            han = chat_queue[x][0]
            hok = chat_queue[x][2]
            hap = chat_queue[x][3]
            QUE = QUE + "\n" + f"**#{x}** - [{han}]({hok}) | `{hap}`"
         await m.reply(QUE, disable_web_page_preview=True)
   else:
      await m.reply("❌ **nothing is currently streaming.**")
