import os
import asyncio

from driver.core import bot, calls, user
from driver.database.dbqueue import remove_active_chat
from driver.queues import (
    QUEUE,
    clear_queue,
    get_queue,
    pop_an_item,
    clean_trash,
)
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pytgcalls.types.input_stream import AudioPiped, AudioVideoPiped
from pytgcalls.types.input_stream.quality import (
    HighQualityAudio,
    HighQualityVideo,
    LowQualityVideo,
    MediumQualityVideo,
)
from pytgcalls.types.stream import StreamAudioEnded, StreamVideoEnded
from pytgcalls.types import Update


keyboard = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton(text="-› تَحَكَمَ", callback_data="stream_menu_panel"),
            InlineKeyboardButton(text="-› اެغِݪاެقِ", callback_data="set_close"),
        ]
    ]
)


async def skip_current_song(chat_id):
    if chat_id in QUEUE:
        chat_queue = get_queue(chat_id)
        if "t.me" in chat_queue[0][2]:
            clean_trash(chat_queue[0][1], chat_id)
        if len(chat_queue) == 1:
            await calls.leave_group_call(chat_id)
            await remove_active_chat(chat_id)
            clear_queue(chat_id)
            return 1
        else:
            try:
                songname = chat_queue[1][0]
                url = chat_queue[1][1]
                link = chat_queue[1][2]
                type = chat_queue[1][3]
                sets = chat_queue[1][4]
                if type == "music":
                    await calls.change_stream(
                        chat_id,
                        AudioPiped(
                            url,
                            HighQualityAudio(),
                        ),
                    )
                elif type == "video":
                    if sets == 720:
                        qual = HighQualityVideo()
                    elif sets == 480:
                        qual = MediumQualityVideo()
                    elif sets == 360:
                        qual = LowQualityVideo()
                    await calls.change_stream(
                        chat_id,
                        AudioVideoPiped(
                            url,
                            HighQualityAudio(),
                            qual,
                        ),
                    )
                pop_an_item(chat_id)
                return [songname, link, type]
            except BaseException as error:
                print(error)
                await calls.leave_group_call(chat_id)
                await remove_active_chat(chat_id)
                clear_queue(chat_id)
                return 2
    else:
        return 0


async def skip_item(chat_id, h):
    if chat_id in QUEUE:
        chat_queue = get_queue(chat_id)
        try:
            x = int(h)
            songname = chat_queue[x][0]
            chat_queue.pop(x)
            return songname
        except Exception as e:
            print(e)
            return 0
    else:
        return 0


@calls.on_kicked()
async def kicked_handler(_, chat_id: int):
    if chat_id in QUEUE:
        await remove_active_chat(chat_id)
        clear_queue(chat_id)


@calls.on_closed_voice_chat()
async def closed_voice_chat_handler(_, chat_id: int):
    if chat_id in QUEUE:
        await remove_active_chat(chat_id)
        clear_queue(chat_id)


@calls.on_left()
async def left_handler(_, chat_id: int):
    if chat_id in QUEUE:
        await remove_active_chat(chat_id)
        clear_queue(chat_id)


@calls.on_stream_end()
async def stream_end_handler(_, u: Update):
    if isinstance(u, StreamAudioEnded) or isinstance(u, StreamVideoEnded):
        chat_id = u.chat_id
        queue = await skip_current_song(chat_id)
        if queue == 1:
            await remove_active_chat(chat_id)
            return
        elif queue == 2:
            await bot.send_message(
                chat_id,
                "❤️‍🔥 حدث خطأ\n\n» **المقاصة** قوائم الانتظار ومغادرة دردشة الفيديو.",
            )
        else:
            await bot.send_message(
                chat_id,
                f"-›  **تَشغِيݪ اެݪاغنية اެݪتي فَي اެݪانتظاࢪ**\n\n-›  **اެݪاެسِمَ:** [{queue[0]}]({queue[1]}) | `{queue[2]}`\n🦴 **اެݪدَࢪدَشِةَ:** `{chat_id}`",
                disable_web_page_preview=True,
                reply_markup=keyboard,
            )
    else:
        pass


async def bash(cmd):
    process = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    err = stderr.decode().strip()
    out = stdout.decode().strip()
    return out, err


def remove_if_exists(path):
    if os.path.exists(path):
        os.remove(path)


async def from_tg_get_msg(url: str):
    data = url.split('/')[-2:]
    if len(data) == 2:
        cid = data[0]
        if cid.isdigit():
            cid = int('-100' + cid)
        mid = int(data[1])
        return await user.get_messages(cid, message_ids=mid)
    return None
