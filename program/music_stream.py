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


import re
import asyncio

from pyrogram import Client
from pyrogram.errors import UserAlreadyParticipant, UserNotParticipant
from pyrogram.types import InlineKeyboardMarkup, Message

from pytgcalls import StreamType
from pytgcalls.types.input_stream import AudioPiped
from pytgcalls.types.input_stream.quality import HighQualityAudio
from pytgcalls.exceptions import NoAudioSourceFound, NoActiveGroupCall, GroupCallNotFound

from program import LOGS
from program.utils.inline import stream_markup
from driver.design.thumbnail import thumb
from driver.design.chatname import CHAT_TITLE
from driver.filters import command, other_filters
from driver.queues import QUEUE, add_to_queue
from driver.core import calls, user, me_user
from driver.utils import bash, remove_if_exists, from_tg_get_msg
from driver.database.dbqueue import add_active_chat, remove_active_chat, music_on
from driver.decorators import require_admin, check_blacklist

from config import BOT_USERNAME, IMG_1, IMG_2, IMG_5
from asyncio.exceptions import TimeoutError
from youtubesearchpython import VideosSearch


def ytsearch(query: str):
    try:
        search = VideosSearch(query, limit=1).result()
        data = search["result"][0]
        songname = data["title"]
        url = data["link"]
        duration = data["duration"]
        thumbnail = data["thumbnails"][0]["url"]
        return [songname, url, duration, thumbnail]
    except Exception as e:
        print(e)
        return 0

async def ytdl(link: str):
    stdout, stderr = await bash(
        f'yt-dlp --geo-bypass -g -f "[height<=?720][width<=?1280]" {link}'
    )
    if stdout:
        return 1, stdout
    return 0, stderr

def convert_seconds(seconds):
    seconds = seconds % (24 * 3600)
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    return "%02d:%02d" % (minutes, seconds)


async def play_tg_file(c: Client, m: Message, replied: Message = None, link: str = None):
    chat_id = m.chat.id
    user_id = m.from_user.id
    if link:
        try:
            replied = await from_tg_get_msg(link)
        except Exception as e:
            LOGS.info(e)
            return await m.reply_text(f"🚫 error:\n\n» {e}")
    if not replied:
        return await m.reply(
            "» reply to an **audio file** or **give something to search.**"
        )
    if replied.audio or replied.voice:
        if not link:
            suhu = await replied.reply("📥 downloading audio...")
        else:
            suhu = await m.reply("📥 downloading audio...")
        dl = await replied.download()
        link = replied.link
        songname = "music"
        thumbnail = f"{IMG_5}"
        duration = "00:00"
        try:
            if replied.audio:
                if replied.audio.title:
                    songname = replied.audio.title[:80]
                else:
                    songname = replied.audio.file_name[:80]
                if replied.audio.thumbs:
                    if not link:
                        thumbnail = await c.download_media(replied.audio.thumbs[0].file_id)
                    else:
                        thumbnail = await user.download_media(replied.audio.thumbs[0].file_id)
                duration = convert_seconds(replied.audio.duration)
            elif replied.voice:
                songname = "voice note"
                duration = convert_seconds(replied.voice.duration)
        except BaseException:
            pass

        if not thumbnail:
            thumbnail = f"{IMG_5}"

        if chat_id in QUEUE:
            await suhu.edit("🔄 Queueing Track...")
            gcname = m.chat.title
            ctitle = await CHAT_TITLE(gcname)
            title = songname
            userid = m.from_user.id
            image = await thumb(thumbnail, title, userid, ctitle)
            pos = add_to_queue(chat_id, songname, dl, link, "music", 0)
            requester = f"[{m.from_user.first_name}](tg://user?id={m.from_user.id})"
            buttons = stream_markup(user_id)
            await suhu.delete()
            await m.reply_photo(
                photo=image,
                reply_markup=InlineKeyboardMarkup(buttons),
                caption=f"💡 **Track added to queue »** `{pos}`\n\n"
                        f"🗂 **Name:** [{songname}]({link}) | `music`\n"
                        f"⏱️ **Duration:** `{duration}`\n"
                        f"🧸 **Request by:** {requester}",
            )
            remove_if_exists(image)
        else:
            try:
                gcname = m.chat.title
                ctitle = await CHAT_TITLE(gcname)
                title = songname
                userid = m.from_user.id
                image = await thumb(thumbnail, title, userid, ctitle)
                await suhu.edit("🔄 Joining Group Call...")
                await music_on(chat_id)
                await add_active_chat(chat_id)
                await calls.join_group_call(
                    chat_id,
                    AudioPiped(
                        dl,
                        HighQualityAudio(),
                    ),
                    stream_type=StreamType().pulse_stream,
                )
                add_to_queue(chat_id, songname, dl, link, "music", 0)
                await suhu.delete()
                buttons = stream_markup(user_id)
                requester = (
                    f"[{m.from_user.first_name}](tg://user?id={m.from_user.id})"
                )
                await m.reply_photo(
                    photo=image,
                    reply_markup=InlineKeyboardMarkup(buttons),
                    caption=f"🗂 **Name:** [{songname}]({link}) | `music`\n"
                            f"⏱️ **Duration:** `{duration}`\n"
                            f"🧸 **Request by:** {requester}",
                )
                remove_if_exists(image)
            except (NoActiveGroupCall, GroupCallNotFound):
                await suhu.delete()
                await remove_active_chat(chat_id)
                await m.reply_text("❌ The bot can't find the Group call or it's inactive.\n\n» Use /startvc command to turn on the Group call !")
            except Exception as e:
                LOGS.info(e)
    else:
        await m.reply_text(
            "» reply to an **audio file** or **give something to search.**"
        )


@Client.on_message(command(["play", f"play@{BOT_USERNAME}"]) & other_filters)
@check_blacklist()
@require_admin(permissions=["can_manage_voice_chats", "can_delete_messages", "can_invite_users"], self=True)
async def audio_stream(c: Client, m: Message):
    await m.delete()
    replied = m.reply_to_message
    chat_id = m.chat.id
    user_id = m.from_user.id
    if m.sender_chat:
        return await m.reply_text(
            "you're an __Anonymous__ user !\n\n» revert back to your real user account to use this bot."
        )
    try:
        ubot = me_user.id
        b = await c.get_chat_member(chat_id, ubot)
        if b.status == "banned":
            try:
                await m.reply_text("❌ The userbot is banned in this chat, unban the userbot first to be able to play music !")
                await remove_active_chat(chat_id)
            except BaseException:
                pass
            invitelink = (await c.get_chat(chat_id)).invite_link
            if not invitelink:
                await c.export_chat_invite_link(chat_id)
                invitelink = (await c.get_chat(chat_id)).invite_link
            if invitelink.startswith("https://t.me/+"):
                invitelink = invitelink.replace(
                    "https://t.me/+", "https://t.me/joinchat/"
                )
            await user.join_chat(invitelink)
            await remove_active_chat(chat_id)
    except UserNotParticipant:
        try:
            invitelink = (await c.get_chat(chat_id)).invite_link
            if not invitelink:
                await c.export_chat_invite_link(chat_id)
                invitelink = (await c.get_chat(chat_id)).invite_link
            if invitelink.startswith("https://t.me/+"):
                invitelink = invitelink.replace(
                    "https://t.me/+", "https://t.me/joinchat/"
                )
            await user.join_chat(invitelink)
            await remove_active_chat(chat_id)
        except UserAlreadyParticipant:
            pass
        except Exception as e:
            LOGS.info(e)
            return await m.reply_text(
                f"❌ **userbot failed to join**\n\n**reason**: `{e}`"
            )
    if replied:
        if replied.audio or replied.voice:
            await play_tg_file(c, m, replied)
        else:
            if len(m.command) < 2:
                await m.reply(
                    "» reply to an **audio file** or **give something to search.**"
                )
            else:
                suhu = await c.send_message(chat_id, "🔍 **Loading...**")
                query = m.text.split(None, 1)[1]
                search = ytsearch(query)
                if search == 0:
                    await suhu.edit("❌ **no results found**")
                else:
                    songname = search[0]
                    title = search[0]
                    url = search[1]
                    duration = search[2]
                    thumbnail = search[3]
                    userid = m.from_user.id
                    gcname = m.chat.title
                    ctitle = await CHAT_TITLE(gcname)
                    image = await thumb(thumbnail, title, userid, ctitle)
                    out, ytlink = await ytdl(url)
                    if out == 0:
                        await suhu.edit(f"❌ yt-dl issues detected\n\n» `{ytlink}`")
                    else:
                        if chat_id in QUEUE:
                            await suhu.edit("🔄 Queueing Track...")
                            pos = add_to_queue(
                                chat_id, songname, ytlink, url, "music", 0
                            )
                            await suhu.delete()
                            buttons = stream_markup(user_id)
                            requester = f"[{m.from_user.first_name}](tg://user?id={m.from_user.id})"
                            await m.reply_photo(
                                photo=image,
                                reply_markup=InlineKeyboardMarkup(buttons),
                                caption=f"💡 **Track added to queue »** `{pos}`\n\n🗂 **Name:** [{songname}]({url}) | `music`\n**⏱ Duration:** `{duration}`\n🧸 **Request by:** {requester}",
                            )
                            remove_if_exists(image)
                        else:
                            try:
                                await suhu.edit("🔄 Joining Group Call...")
                                await music_on(chat_id)
                                await add_active_chat(chat_id)
                                await calls.join_group_call(
                                    chat_id,
                                    AudioPiped(
                                        ytlink,
                                        HighQualityAudio(),
                                    ),
                                    stream_type=StreamType().local_stream,
                                )
                                add_to_queue(chat_id, songname, ytlink, url, "music", 0)
                                await suhu.delete()
                                buttons = stream_markup(user_id)
                                requester = (
                                    f"[{m.from_user.first_name}](tg://user?id={m.from_user.id})"
                                )
                                await m.reply_photo(
                                    photo=image,
                                    reply_markup=InlineKeyboardMarkup(buttons),
                                    caption=f"🗂 **Name:** [{songname}]({url}) | `music`\n**⏱ Duration:** `{duration}`\n🧸 **Request by:** {requester}",
                                )
                                remove_if_exists(image)
                            except (NoActiveGroupCall, GroupCallNotFound):
                                await suhu.delete()
                                await remove_active_chat(chat_id)
                                await m.reply_text("❌ The bot can't find the Group call or it's inactive.\n\n» Use /startvc command to turn on the Group call !")
                            except NoAudioSourceFound:
                                await suhu.delete()
                                await remove_active_chat(chat_id)
                                await m.reply_text("❌ The content you provide to play has no audio source")
    else:
        if len(m.command) < 2:
            await m.reply(
                "» reply to an **audio file** or **give something to search.**"
            )
        elif "t.me" in m.command[1]:
            for i in m.command[1:]:
                if "t.me" in i:
                    await play_tg_file(c, m, link=i)
                continue
        else:
            suhu = await c.send_message(chat_id, "🔍 **Loading...**")
            query = m.text.split(None, 1)[1]
            search = ytsearch(query)
            if search == 0:
                await suhu.edit("❌ **no results found**")
            else:
                songname = search[0]
                title = search[0]
                url = search[1]
                duration = search[2]
                thumbnail = search[3]
                userid = m.from_user.id
                gcname = m.chat.title
                ctitle = await CHAT_TITLE(gcname)
                image = await thumb(thumbnail, title, userid, ctitle)
                veez, ytlink = await ytdl(url)
                if veez == 0:
                    await suhu.edit(f"❌ yt-dl issues detected\n\n» `{ytlink}`")
                else:
                    if chat_id in QUEUE:
                        await suhu.edit("🔄 Queueing Track...")
                        pos = add_to_queue(chat_id, songname, ytlink, url, "music", 0)
                        await suhu.delete()
                        requester = f"[{m.from_user.first_name}](tg://user?id={m.from_user.id})"
                        buttons = stream_markup(user_id)
                        await m.reply_photo(
                            photo=image,
                            reply_markup=InlineKeyboardMarkup(buttons),
                            caption=f"💡 **Track added to queue »** `{pos}`\n\n🗂 **Name:** [{songname}]({url}) | `music`\n**⏱ Duration:** `{duration}`\n🧸 **Request by:** {requester}",
                        )
                        remove_if_exists(image)
                    else:
                        try:
                            await suhu.edit("🔄 Joining Group Call...")
                            await music_on(chat_id)
                            await add_active_chat(chat_id)
                            await calls.join_group_call(
                                chat_id,
                                AudioPiped(
                                    ytlink,
                                    HighQualityAudio(),
                                ),
                                stream_type=StreamType().local_stream,
                            )
                            add_to_queue(chat_id, songname, ytlink, url, "music", 0)
                            await suhu.delete()
                            requester = f"[{m.from_user.first_name}](tg://user?id={m.from_user.id})"
                            buttons = stream_markup(user_id)
                            await m.reply_photo(
                                photo=image,
                                reply_markup=InlineKeyboardMarkup(buttons),
                                caption=f"🗂 **Name:** [{songname}]({url}) | `music`\n**⏱ Duration:** `{duration}`\n🧸 **Request by:** {requester}",
                            )
                            remove_if_exists(image)
                        except (NoActiveGroupCall, GroupCallNotFound):
                            await suhu.delete()
                            await remove_active_chat(chat_id)
                            await m.reply_text("❌ The bot can't find the Group call or it's inactive.\n\n» Use /startvc command to turn on the Group call !")
                        except NoAudioSourceFound:
                            await suhu.delete()
                            await remove_active_chat(chat_id)
                            await m.reply_text("❌ The content you provide to play has no audio source.\n\n» Try to play another song or try again later !")


@Client.on_message(command(["stream", f"stream@{BOT_USERNAME}"]) & other_filters)
@check_blacklist()
@require_admin(permissions=["can_manage_voice_chats", "can_delete_messages", "can_invite_users"], self=True)
async def live_music_stream(c: Client, m: Message):
    await m.delete()
    chat_id = m.chat.id
    user_id = m.from_user.id
    if m.sender_chat:
        return await m.reply_text(
            "you're an __Anonymous__ user !\n\n» revert back to your real user account to use this bot."
        )
    try:
        ubot = me_user.id
        b = await c.get_chat_member(chat_id, ubot)
        if b.status == "banned":
            try:
                await m.reply_text("❌ The userbot is banned in this chat, unban the userbot first to be able to play music !")
                await remove_active_chat(chat_id)
            except BaseException:
                pass
            invitelink = (await c.get_chat(chat_id)).invite_link
            if not invitelink:
                await c.export_chat_invite_link(chat_id)
                invitelink = (await c.get_chat(chat_id)).invite_link
            if invitelink.startswith("https://t.me/+"):
                invitelink = invitelink.replace(
                    "https://t.me/+", "https://t.me/joinchat/"
                )
            await user.join_chat(invitelink)
            await remove_active_chat(chat_id)
    except UserNotParticipant:
        try:
            invitelink = (await c.get_chat(chat_id)).invite_link
            if not invitelink:
                await c.export_chat_invite_link(chat_id)
                invitelink = (await c.get_chat(chat_id)).invite_link
            if invitelink.startswith("https://t.me/+"):
                invitelink = invitelink.replace(
                    "https://t.me/+", "https://t.me/joinchat/"
                )
            await user.join_chat(invitelink)
            await remove_active_chat(chat_id)
        except UserAlreadyParticipant:
            pass
        except Exception as e:
            LOGS.info(e)
            return await m.reply_text(
                f"❌ **userbot failed to join**\n\n**reason**: `{e}`"
            )
    if len(m.command) < 2:
        await m.reply_text("» Give me a youtube live url/m3u8 url to stream.")
    else:
        url = m.text.split(None, 1)[1]
        msg = await m.reply_text("🔍 **Loading...**")
        regex = r"^(https?\:\/\/)?(www\.youtube\.com|youtu\.?be)\/.+"
        match = re.match(regex, url)
        if match:
            coda, data = await ytdl(url)
        else:
            data = url
            coda = 1
        if coda == 0:
            await msg.edit_text(f"❌ yt-dl issues detected\n\n» `{data}`")
        else:
            if "m3u8" in url:
                if chat_id in QUEUE:
                    await msg.edit_text("🔄 Queueing Track...")
                    pos = add_to_queue(chat_id, "m3u8 audio", data, url, "music", 0)
                    await msg.delete()
                    requester = f"[{m.from_user.first_name}](tg://user?id={m.from_user.id})"
                    buttons = stream_markup(user_id)
                    await m.reply_photo(
                        photo=f"{IMG_1}",
                        reply_markup=InlineKeyboardMarkup(buttons),
                        caption=f"💡 **Track added to queue »** `{pos}`\n\n🗂 **Name:** [m3u8 audio stream]({url}) | `live`\n🧸 **Requested by:** {requester}",
                    )
                else:
                    try:
                        await msg.edit_text("🔄 Joining Group Call...")
                        await music_on(chat_id)
                        await add_active_chat(chat_id)
                        await calls.join_group_call(
                            chat_id,
                            AudioPiped(
                                data,
                                HighQualityAudio(),
                            ),
                            stream_type=StreamType().live_stream,
                        )
                        add_to_queue(chat_id, "m3u8 audio", data, url, "music", 0)
                        await msg.delete()
                        requester = f"[{m.from_user.first_name}](tg://user?id={m.from_user.id})"
                        buttons = stream_markup(user_id)
                        await m.reply_photo(
                            photo=f"{IMG_2}",
                            reply_markup=InlineKeyboardMarkup(buttons),
                            caption=f"🗂 **Name:** [m3u8 audio stream]({url}) | `live`\n🧸 **Requested by:** {requester}",
                        )
                    except (NoActiveGroupCall, GroupCallNotFound):
                        await msg.delete()
                        await remove_active_chat(chat_id)
                        await m.reply_text("❌ The bot can't find the Group call or it's inactive.\n\n» Use /startvc command to turn on the Group call !")
                    except NoAudioSourceFound:
                        await msg.delete()
                        await remove_active_chat(chat_id)
                        await m.reply_text("❌ The content you provide to play has no audio source")
            else:
                search = ytsearch(url)
                title = search[0]
                songname = search[0]
                thumbnail = search[3]
                userid = m.from_user.id
                gcname = m.chat.title
                ctitle = await CHAT_TITLE(gcname)
                image = await thumb(thumbnail, title, userid, ctitle)
                if chat_id in QUEUE:
                    await msg.edit_text("🔄 Queueing Track...")
                    pos = add_to_queue(chat_id, songname, data, url, "music", 0)
                    await msg.delete()
                    requester = f"[{m.from_user.first_name}](tg://user?id={m.from_user.id})"
                    buttons = stream_markup(user_id)
                    await m.reply_photo(
                        photo=image,
                        reply_markup=InlineKeyboardMarkup(buttons),
                        caption=f"💡 **Track added to queue »** `{pos}`\n\n🗂 **Name:** [{songname}]({url}) | `live`\n🧸 **Requested by:** {requester}",
                    )
                    remove_if_exists(image)
                else:
                    try:
                        await msg.edit_text("🔄 Joining Group Call...")
                        await music_on(chat_id)
                        await add_active_chat(chat_id)
                        await calls.join_group_call(
                            chat_id,
                            AudioPiped(
                                data,
                                HighQualityAudio(),
                            ),
                            stream_type=StreamType().live_stream,
                        )
                        add_to_queue(chat_id, songname, data, url, "music", 0)
                        await msg.delete()
                        requester = f"[{m.from_user.first_name}](tg://user?id={m.from_user.id})"
                        buttons = stream_markup(user_id)
                        await m.reply_photo(
                            photo=image,
                            reply_markup=InlineKeyboardMarkup(buttons),
                            caption=f"🗂 **Name:** [{songname}]({url}) | `live`\n🧸 **Requested by:** {requester}",
                        )
                        remove_if_exists(image)
                    except (NoActiveGroupCall, GroupCallNotFound):
                        await msg.delete()
                        await remove_active_chat(chat_id)
                        await m.reply_text("❌ The bot can't find the Group call or it's inactive.\n\n» Use /startvc command to turn on the Group call !")
                    except NoAudioSourceFound:
                        await msg.delete()
                        await remove_active_chat(chat_id)
                        await m.reply_text("❌ The content you provide to play has no audio source")
                    except TimeoutError:
                        await msg.delete()
                        await remove_active_chat(chat_id)
                        await m.reply_text("The process was cancelled, please try again later or use `/vstream` command to stream in audio only.")
