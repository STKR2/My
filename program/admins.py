from config import BOT_USERNAME
from cache.admins import admins
from pyrogram.types import Message
from driver.filters import command, other_filters
from pyrogram import Client, filters
from driver.veez import call_py, bot
from driver.queues import QUEUE, clear_queue
from driver.decorators import authorized_users_only
from driver.utils import skip_current_song, skip_item


@Client.on_message(command(["reload", f"reload@{BOT_USERNAME}"]) & other_filters)
@authorized_users_only
async def update_admin(client, message):
    global admins
    new_admins = []
    new_ads = await client.get_chat_members(message.chat.id, filter="administrators")
    for u in new_ads:
        new_admins.append(u.user.id)
    admins[message.chat.id] = new_admins
    await message.reply_text(
        "✅ Bot **reloaded correctly !**\n✅ **Admin list** has been **updated !**"
    )


@Client.on_message(command(["skip", f"skip@{BOT_USERNAME}"]) & other_filters)
@authorized_users_only
async def skip(client, m: Message):
   chat_id = m.chat.id
   if len(m.command) < 2:
      op = await skip_current_song(chat_id)
      if op==0:
         await m.reply("❌ nothing is currently playing")
      elif op==1:
         await m.reply("✅ __Queues__ is empty.\n\n• userbot leaving voice chat")
      else:
         await m.reply(f"⏭ **Skipped streaming.**\n\n💡 **now playing:** [{op[0]}]({op[1]}) | `{op[2]}`", disable_web_page_preview=True)
   else:
      skip = m.text.split(None, 1)[1]
      OP = "🗑 **removed song from queue:**"
      if chat_id in QUEUE:
         items = [int(x) for x in skip.split(" ") if x.isdigit()]
         items.sort(reverse=True)
         for x in items:
            if x==0:
               pass
            else:
               hm = await skip_item(chat_id, x)
               if hm==0:
                  pass
               else:
                  OP = OP + "\n" + f"**#{x}** - {hm}"
         await m.reply(OP)


@Client.on_message(command(["stop", f"stop@{BOT_USERNAME}", "end", f"end@{BOT_USERNAME}"]) & other_filters)
@authorized_users_only
async def stop(client, m: Message):
   chat_id = m.chat.id
   if chat_id in QUEUE:
      try:
         await call_py.leave_group_call(chat_id)
         clear_queue(chat_id)
         await m.reply("✅ **streaming has ended.**")
      except Exception as e:
         await m.reply(f"**ERROR:** \n`{e}`")
   else:
      await m.reply("❌ **nothing in streaming**")


@Client.on_message(command(["pause", f"pause@{BOT_USERNAME}"]) & other_filters)
@authorized_users_only
async def pause(client, m: Message):
   chat_id = m.chat.id
   if chat_id in QUEUE:
      try:
         await call_py.pause_stream(chat_id)
         await m.reply("⏸️ **streaming has paused**")
      except Exception as e:
         await m.reply(f"**ERROR:** \n`{e}`")
   else:
      await m.reply("❌ **nothing in streaming**")


@Client.on_message(command(["resume", f"resume@{BOT_USERNAME}"]) & other_filters)
@authorized_users_only
async def resume(client, m: Message):
   chat_id = m.chat.id
   if chat_id in QUEUE:
      try:
         await call_py.resume_stream(chat_id)
         await m.reply("▶ **streaming has resumed.**")
      except Exception as e:
         await m.reply(f"**ERROR:** \n`{e}`")
   else:
      await m.reply("❌ **nothing in streaming**")
