# Copyright (C) 2021 By VeezMusicProject


from pyrogram import Client as app
from pyrogram.types import Message
from youtube_search import YoutubeSearch
from config import Veez
from helpers.filters import command

@app.on_message(command(["search", f"search@{Veez.BOT_USERNAME}"]))
async def ytsearch(_, message: Message):
    m = await message.reply_text("🔎 **searching url...**")
    try:
        if len(message.command) < 2:
            await message.reply_text("`/search` needs an argument!")
            return
        query = message.text.split(None, 1)[1]
        results = YoutubeSearch(query, max_results=5).to_dict()
        i = 0
        text = ""
        while i < 5:
            text += f"**Name:** `{results[i]['title']}`\n"
            text += f"**Duration:** {results[i]['duration']}\n"
            text += f"**Views:** {results[i]['views']}\n"
            text += f"**Channel:** {results[i]['channel']}\n"
            text += f"https://www.youtube.com{results[i]['url_suffix']}\n\n"
            i += 1
        await m.edit(text, disable_web_page_preview=True)
    except Exception as e:
        await m.edit(str(e))
