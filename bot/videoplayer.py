# Copyright (C) 2021 By VeezMusicProject

import os
import asyncio
import subprocess
from pytgcalls import idle
from pytgcalls.pytgcalls import PyTgCalls
from pytgcalls import StreamType
from pytgcalls.types import Update
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram import Client, filters
from pyrogram.types import Message
from config import Veez
from helpers.decorators import authorized_users_only
from helpers.filters import command
from helpers.loggings import LOG
from youtube_dl import YoutubeDL
from youtube_dl.utils import ExtractorError
from pytgcalls.types.input_stream import (
    VideoParameters,
    AudioParameters,
    InputAudioStream,
    InputVideoStream
)

SIGINT: int = 2

app = Client(Veez.SESSION_NAME, Veez.API_ID, Veez.API_HASH)
call_py = PyTgCalls(app)
FFMPEG_PROCESS = {}


def convert_seconds(seconds: int) -> str:
    seconds = seconds % (24 * 3600)
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    return "%02d:%02d" % (minutes, seconds)


def raw_converter(dl, song, video):
    return subprocess.Popen(
        ['ffmpeg', '-i', dl, '-f', 's16le', '-ac', '1', '-ar', '48000', song, '-y', '-f', 'rawvideo', '-r', '20', '-pix_fmt', 'yuv420p', '-vf', 'scale=854:480', video, '-y'],
        stdin=None,
        stdout=None,
        stderr=None,
        cwd=None,
    )

async def leave_call(chat_id: int):
    process = FFMPEG_PROCESS.get(chat_id)
    if process:
        try:
            process.send_signal(SIGINT)
            await asyncio.sleep(3)
        except Exception as e:
            print(e)
            pass
    try:
        await call_py.leave_group_call(chat_id)
    except Exception as e:
        print(f"🚫 error - {e}")

def youtube(url: str):
    try:
        params = {"format": "best[height=?480]/best", "noplaylist": True}
        yt = YoutubeDL(params)
        info = yt.extract_info(url, download=False)
        return info['url'], info['title'], info['duration']
    except ExtractorError:
        return None, None
    except Exception:
        return None, None


@Client.on_message(command(["vplay", f"vplay@{Veez.BOT_USERNAME}"]) & filters.group & ~filters.edited)
@authorized_users_only
async def startvideo(client, m: Message):
    
    keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="✨ ɢʀᴏᴜᴘ",
                        url="https://t.me/VeezSupportGroup"),
                    InlineKeyboardButton(
                        text="🌻 ᴄʜᴀɴɴᴇʟ",
                        url="https://t.me/levinachannel")
                ]
            ]
        )
    
    replied = m.reply_to_message
    if not replied:
        if len(m.command) < 2:
            await m.reply("💡 **reply to video or provide youtube/live video url to start video streaming**")
        else:
            livelink = m.text.split(None, 1)[1]
            chat_id = m.chat.id
            try:
                livelink, title, duration = await asyncio.wait_for(
                    app.loop.run_in_executor(
                        None,
                        lambda : youtube(livelink)
                    ),
                    timeout=None
                )
            except asyncio.TimeoutError:
                await m.reply("TimeoutError: process is taking unexpected time")
                return
            if not livelink:
                await m.reply("failed to get video data")
                return
            process = raw_converter(livelink, f'audio{chat_id}.raw', f'video{chat_id}.raw')
            FFMPEG_PROCESS[chat_id] = process
            msg = await m.reply("🔁 **starting video streaming...**")
            await asyncio.sleep(10)
            try:
                audio_file = f'audio{chat_id}.raw'
                video_file = f'video{chat_id}.raw'
                while not os.path.exists(audio_file) or \
                        not os.path.exists(video_file):
                    await asyncio.sleep(2)
                await call_py.join_group_call(
                    chat_id,
                    InputAudioStream(
                        audio_file,
                        AudioParameters(
                            bitrate=48000,
                        ),
                    ),
                    InputVideoStream(
                        video_file,
                        VideoParameters(
                            width=854,
                            height=480,
                            frame_rate=20,
                        ),
                    ),
                    stream_type=StreamType().local_stream,
                )
                await m.reply_photo(
                    photo="https://telegra.ph/file/422650a849a8d6831bde8.png",
                    reply_markup=keyboard,
                    caption=f"💡 **video streaming started!**\n\n🏷 **Name:** {title}\n⏱ **Duration:** `{convert_seconds(duration)} m`\n\n» **join to video chat on the top to watch the video.**")
                return await msg.delete()
                await idle()
            except Exception as e:
                await msg.edit(f"🚫 **error** | `{e}`")
   
    elif replied.video or replied.document:
        msg = await m.reply("📥 downloading video...")
        video = await client.download_media(m.reply_to_message)
        chat_id = m.chat.id
        await msg.edit("🔁 **preparing video...**")
        os.system(f"ffmpeg -i '{video}' -f s16le -ac 1 -ar 48000 'audio{chat_id}.raw' -y -f rawvideo -r 20 -pix_fmt yuv420p -vf scale=640:360 'video{chat_id}.raw' -y")
        try:
            audio_file = f'audio{chat_id}.raw'
            video_file = f'video{chat_id}.raw'
            while not os.path.exists(audio_file) or \
                    not os.path.exists(video_file):
                await asyncio.sleep(2)
            await call_py.join_group_call(
                chat_id,
                InputAudioStream(
                    audio_file,
                    AudioParameters(
                        bitrate=48000,
                    ),
                ),
                InputVideoStream(
                    video_file,
                    VideoParameters(
                        width=640,
                        height=360,
                        frame_rate=20,
                    ),
                ),
                stream_type=StreamType().local_stream,
            )
            await m.reply_photo(
                photo="https://telegra.ph/file/dc90e91cc77e68568e7b4.png",
                reply_markup=keyboard,
                caption=f"💡 **video streaming started !**\n\n» **join to video chat on the top to watch the video.**")
            return await msg.delete()
        except Exception as e:
            await msg.edit(f"🚫 **error** | `{e}`")
            await idle()
    else:
        await m.reply("💭 please reply to video or video file to stream")


@Client.on_message(command(["vstop", f"vstop@{Veez.BOT_USERNAME}"]) & filters.group & ~filters.edited)
@authorized_users_only
async def stopvideo(client, m: Message):
    chat_id = m.chat.id
    try:
        process = FFMPEG_PROCESS.get(chat_id)
        if process:
            try:
                process.send_signal(SIGINT)
                await asyncio.sleep(3)
            except Exception as e:
                print(e)
                pass
        await call_py.leave_group_call(chat_id)
        await m.reply("✅ **successfully left vc !**")
    except Exception as e:
        await m.reply(f"🚫 **error** | `{e}`")

@call_py.on_stream_end()
async def handler(client: PyTgCalls, update: Update):
    LOG.info(f"called ended stream")
    chat_id = update.chat_id
    await call_py.leave_group_call(chat_id) 


@Client.on_message(command(["cplay", f"cplay@{Veez.BOT_USERNAME}"]) & filters.group & ~filters.edited)
@authorized_users_only
async def chstream(client, m: Message):
    replied = m.reply_to_message
    if not replied:
        if len(m.command) < 2:
            await m.reply("💡 **reply to video or provide youtube/live video url to start video streaming**")
        else:
            livelink = m.text.split(None, 1)[1]
            chat_id = Veez.CHANNEL
            try:
                livelink = await asyncio.wait_for(
                    app.loop.run_in_executor(
                        None,
                        lambda : youtube(livelink)
                    ),
                    timeout=None
                )
            except asyncio.TimeoutError:
                await m.reply("TimeoutError: process is taking unexpected time")
                return
            if not livelink:
                await m.reply("failed to get video data")
                return
            process = raw_converter(livelink, f'audio{chat_id}.raw', f'video{chat_id}.raw')
            FFMPEG_PROCESS[chat_id] = process
            msg = await m.reply("🔁 **starting video streaming...**")
            await asyncio.sleep(10)
            try:
                audio_file = f'audio{chat_id}.raw'
                video_file = f'video{chat_id}.raw'
                while not os.path.exists(audio_file) or \
                        not os.path.exists(video_file):
                    await asyncio.sleep(2)
                await call_py.join_group_call(
                    chat_id,
                    InputAudioStream(
                        audio_file,
                        AudioParameters(
                            bitrate=48000,
                        ),
                    ),
                    InputVideoStream(
                        video_file,
                        VideoParameters(
                            width=854,
                            height=480,
                            frame_rate=20,
                        ),
                    ),
                    stream_type=StreamType().local_stream,
                )
                await msg.edit("💡 **video streaming channel started !**")
                await idle()
            except Exception as e:
                await msg.edit(f"🚫 **error** - `{e}`")
   
    elif replied.video or replied.document:
        msg = await m.reply("📥 **downloading video...**")
        video = await client.download_media(m.reply_to_message)
        chat_id = Veez.CHANNEL
        await msg.edit("🔁 **preparing video...**")
        os.system(f"ffmpeg -i '{video}' -f s16le -ac 1 -ar 48000 'audio{chat_id}.raw' -y -f rawvideo -r 20 -pix_fmt yuv420p -vf scale=640:360 'video{chat_id}.raw' -y")
        try:
            audio_file = f'audio{chat_id}.raw'
            video_file = f'video{chat_id}.raw'
            while not os.path.exists(audio_file) or \
                    not os.path.exists(video_file):
                await asyncio.sleep(2)
            await call_py.join_group_call(
                chat_id,
                InputAudioStream(
                    audio_file,
                    AudioParameters(
                        bitrate=48000,
                    ),
                ),
                InputVideoStream(
                    video_file,
                    VideoParameters(
                        width=640,
                        height=360,
                        frame_rate=20,
                    ),
                ),
                stream_type=StreamType().local_stream,
            )
            await msg.edit("💡 **video streaming channel started !**")
        except Exception as e:
            await msg.edit(f"🚫 **error** - `{e}`")
            await idle()
    else:
        await m.reply("💭 **please reply to video or video file to stream**")


@Client.on_message(command(["cstop", f"cstop@{Veez.BOT_USERNAME}"]) & filters.group & ~filters.edited)
@authorized_users_only
async def chstopvideo(client, m: Message):
    chat_id = Veez.CHANNEL
    try:
        process = FFMPEG_PROCESS.get(chat_id)
        if process:
            try:
                process.send_signal(SIGINT)
                await asyncio.sleep(3)
            except Exception as e:
                print(e)
                pass
        await call_py.leave_group_call(chat_id)
        await m.reply("✅ **video streaming channel ended**")
    except Exception as e:
        await m.reply(f"🚫 **error** - `{e}`")
