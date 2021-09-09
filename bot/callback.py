from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from config import ASSISTANT_NAME as bn


@Client.on_callback_query(filters.regex("cbguide"))
async def cbguide(_, query: CallbackQuery):
    await query.edit_message_text(
        f"""❓ HOW TO USE THIS BOT:

1.) first, add me to your group.
2.) then promote me as admin and give all permissions except anonymous admin.
3.) add @{bn} to your group.
4.) turn on the voice chat first before start to stream video.
5.) type /vstream (reply to video) to start streaming.
6.) type /vstop to end the video streaming.

📝 **note: stream & stop command can only be executed by group admin only!**

⚡ __Maintained by Veez Project Team__""",
        reply_markup=InlineKeyboardMarkup(
            [[
                InlineKeyboardButton(
                    "🏡 Go Back", callback_data="cbstart")
            ]]
        ))


@Client.on_callback_query(filters.regex("cbstart"))
async def cbstart(_, query: CallbackQuery):
    await query.edit_message_text(
        f"✨ **Hello there, I am a telegram group video streaming bot.**\n\n💭 **I was created to stream videos in group "
        f"video chats easily.**\n\n❔ **To find out how to use me, please press the help button below** 👇🏻",
        reply_markup=InlineKeyboardMarkup(
            [[
                InlineKeyboardButton(
                    "❔ HOW TO USE THIS BOT", callback_data="cbguide")
            ], [
                InlineKeyboardButton(
                    "🌐 Terms & Condition", callback_data="cbinfo")
            ], [
                InlineKeyboardButton(
                    "💬 Group", url="https://t.me/VeezSupportGroup"),
                InlineKeyboardButton(
                    "📣 Channel", url="https://t.me/levinachannel")
            ], [
                InlineKeyboardButton(
                    "👩🏻‍💻 Developer", url="https://t.me/dlwrml")
            ], [
                InlineKeyboardButton(
                    "📚 All Command List", callback_data="cblist")
            ]]
        ))


@Client.on_callback_query(filters.regex("cbinfo"))
async def cbinfo(_, query: CallbackQuery):
    await query.edit_message_text(
        f"""🌐 **bot information !**

🤖 __This bot was created to stream video in telegram group video chats using several methods from WebRTC.__

💡 __Powered by PyTgcalls the Async client API for the Telegram Group Calls, and Pyrogram the telegram MTProto API 
Client Library and Framework in Pure Python for Users and Bots.__ 

👨🏻‍💻 __Thanks to the developers who participated in the development of this bot, the list of devs can be seen below:__

👩🏻‍✈️ » [Levina Shavila](https://github.com/levina-lab)
🤵🏻 » [Sammy-XD](https://github.com/Sammy-XD)
👩🏻‍✈️ » [Achu Biju](https://github.com/Achu2234)
🤵🏻 » [Zxce3](https://github.com/Zxce3)
🤵🏻 » [Tofik Denianto](https://github.com/tofikdn)
🤵🏻 » [Shohih Abdul](https://github.com/DoellBarr)

__This bot licensed under GNU-GPL 3.0 License__""",
        reply_markup=InlineKeyboardMarkup(
            [[
                InlineKeyboardButton(
                    "🏡 Go Back", callback_data="cbstart")
            ]]
        ),
        disable_web_page_preview=True
    )


@Client.on_callback_query(filters.regex("cblist"))
async def cblist(_, query: CallbackQuery):
    await query.edit_message_text(
        f"""📚 All Command List:

» /vstream (reply to video or yt url) - to stream video
» /vstop - end the video streaming
» /song (song name) - download song from YT
» /vsong (video name) - download video from YT
» /lyric (song name) - lyric scrapper

🎊 FUN CMD:

» /asupan - check it by yourself
» /chika - check it by yourself
» /wibu - check it by yourself
» /truth - check it by yourself
» /dare - check it by yourself

🔰 EXTRA CMD:

» /tts (reply to text) - text to speech
» /alive - check bot alive status
» /ping - check bot ping status
» /uptime - check bot uptime status
» /sysinfo - check bot system information

⚡ __Maintained by Veez Project Team__""",
        reply_markup=InlineKeyboardMarkup(
            [[
                InlineKeyboardButton(
                    "🏡 Go Back", callback_data="cbstart")
            ]]
        ))


@Client.on_callback_query(filters.regex("cls"))
async def close(_, query: CallbackQuery):
    await query.message.delete()
