import os
import re
import pafy
import time
import asyncio
import ffmpeg
from asyncio import sleep

from pyrogram import Client, filters
from pyrogram.types import Message
from pytgcalls import GroupCallFactory
from youtube_dl import YoutubeDL

from config import API_ID, API_HASH, SESSION_NAME, BOT_USERNAME
from helpers.decorators import authorized_users_only
from helpers.filters import command


ydl_opts = {
    "geo-bypass": True,
    "nocheckcertificate": True,
}
ydl = YoutubeDL(ydl_opts)

STREAM = {8}
VIDEO_CALL = {}

app = Client(
    SESSION_NAME,
    api_id=API_ID,
    api_hash=API_HASH,
)
group_call_factory = GroupCallFactory(app, GroupCallFactory.MTPROTO_CLIENT_TYPE.PYROGRAM)


@Client.on_message(command(["vstream", f"vstream@{BOT_USERNAME}"]) & filters.group & ~filters.edited)
@authorized_users_only
async def stream(client, m: Message):
    replied = m.reply_to_message
    if not replied:
        if len(m.command) < 2:
            await m.reply("💡 reply to video or provide youtube video url to start video streaming")
        else:
            video = m.text.split(None, 1)[1]
            youtube_regex = (
                                         r'(https?://)?(www\.)?'
                                       '(youtube|youtu|youtube-nocookie)\.(com|be)/'
                                       '(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})')
            youtube_regex_match = re.match(youtube_regex, video)
            if youtube_regex_match:
            	try:
            		yt = pafy.new(video)
            		best = yt.getbest()
            		video_url = best.url
            	except Exception as e:
            		await m.reply(f"🚫 **error** - `{e}`")
            		return
            	msg = await m.reply("🔁 **starting video streaming...**")
            	chat_id = m.chat.id
            	await asyncio.sleep(1)
            	try:
            	   group_call = group_call_factory.get_group_call()
            	   await group_call.join(chat_id)
            	   await group_call.start_video(video_url, repeat=False)
            	   VIDEO_CALL[chat_id] = group_call
            	   await msg.edit((f"💡 **started [video streaming]({video_url}) !\n\n» join to video chat on the top to watch streaming."), disable_web_page_preview=True)
            	except Exception as e:
            		await msg.edit(f"**Error** -- `{e}`")
            else:
            	msg = await m.reply("🔁 **starting video streaming...**")
            	chat_id = m.chat.id
            	await asyncio.sleep(1)
            	try:
            	   group_call = group_call_factory.get_group_call()
            	   await group_call.join(chat_id)
            	   await group_call.start_video(video, repeat=False)
            	   VIDEO_CALL[chat_id] = group_call
            	   await msg.edit((f"💡 **started [video streaming]({video}) !\n\n» join to video chat on the top to watch streaming."), disable_web_page_preview=True)
            	except Exception as e:
            		await msg.edit(f"**🚫 error** - `{e}`")
            	
    elif replied.video or replied.document:
        msg = await m.reply("📥 downloading video...")
        video = await client.download_media(m.reply_to_message)
        chat_id = m.chat.id
        await asyncio.sleep(2)
        try:
            group_call = group_call_factory.get_group_call()
            await group_call.join(chat_id)
            await group_call.start_video(video)
            VIDEO_CALL[chat_id] = group_call
            await msg.edit("💡 **video streaming started!**\n\n» **join to video chat to watch the video.**")
        except Exception as e:
            await msg.edit(f"**🚫 error** - `{e}`")
    else:
        await m.reply("💭 please reply to video or video file to stream")


@Client.on_message(command(["vstop", f"vstop@{BOT_USERNAME}"]) & filters.group & ~filters.edited)
@authorized_users_only
async def stopvideo(client, m: Message):
    chat_id = m.chat.id
    try:
        await VIDEO_CALL[chat_id].stop()
        await m.reply("✅ **streaming has ended successfully !**")
    except Exception as e:
        await m.reply(f"🚫 **error** - `{e}`")
