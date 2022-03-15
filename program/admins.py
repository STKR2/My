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


import traceback

from cache.admins import admins
from config import BOT_USERNAME, IMG_5

from driver.core import calls, me_user
from driver.design.thumbnail import thumb
from driver.design.chatname import CHAT_TITLE
from driver.queues import QUEUE, clear_queue
from driver.filters import command, other_filters
from driver.decorators import authorized_users_only, check_blacklist, require_admin
from driver.utils import skip_current_song, skip_item, remove_if_exists, R
from driver.database.dbqueue import (
    is_music_playing,
    remove_active_chat,
    music_off,
    music_on,
)

from pyrogram import Client, filters
from program.utils.inline import stream_markup, close_mark
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardMarkup,
    Message,
)


@Client.on_message(command(["reload", f"reload@{BOT_USERNAME}"]) & other_filters)
@authorized_users_only
@check_blacklist()
async def update_admin(client, message: Message):
    global admins
    new_admins = []
    new_ads = await client.get_chat_members(message.chat.id, filter="administrators")
    for u in new_ads:
        new_admins.append(u.user.id)
    admins[message.chat.id] = new_admins
    await message.reply_text(
        f"✅ {R('bot_reload')}\n"
        f"✅ {R('admin_update')}"
    )


@Client.on_message(
    command(["stop", f"stop@{BOT_USERNAME}", "end", f"end@{BOT_USERNAME}", "vstop"])
    & other_filters
)
@authorized_users_only
@check_blacklist()
async def stop(client, m: Message):
    chat_id = m.chat.id
    if chat_id in QUEUE:
        try:
            await calls.leave_group_call(chat_id)
            await remove_active_chat(chat_id)
            clear_queue(chat_id)
            await m.reply_text(f"✅ {R('bot_disconnect')}")
        except Exception as e:
            traceback.print_exc()
            await m.reply_text(f"🚫 **{R('error')}**\n\n`{e}`")
    else:
        await m.reply_text(f"❌ **{R('play_nothing')}**")


@Client.on_message(
    command(["pause", f"pause@{BOT_USERNAME}", "vpause"]) & other_filters
)
@authorized_users_only
@check_blacklist()
async def pause(client, m: Message):
    chat_id = m.chat.id
    if chat_id in QUEUE:
        try:
            if not await is_music_playing(chat_id):
                return await m.reply_text(f"ℹ️ {R('play_paused')}")
            await calls.pause_stream(chat_id)
            await music_off(chat_id)
            await m.reply_text(
                f"⏸ **{R('play_pause')}**\n\n"
                f"• **{R('play_to_resume')}**\n"
                f"» /resume {R('command')}"
            )
        except Exception as e:
            traceback.print_exc()
            await m.reply(f"🚫 **{R('error')}**\n\n`{e}`")
    else:
        await m.reply(f"❌ **{R('play_nothing')}**")


@Client.on_message(
    command(["resume", f"resume@{BOT_USERNAME}", "vresume"]) & other_filters
)
@authorized_users_only
@check_blacklist()
async def resume(client, m: Message):
    chat_id = m.chat.id
    if chat_id in QUEUE:
        try:
            if await is_music_playing(chat_id):
                return await m.reply_text(f"ℹ️ {R('play_resumed')}")
            await calls.resume_stream(chat_id)
            await music_on(chat_id)
            await m.reply_text(
                f"▶️ **{R('play_resume')}**\n\n"
                f"• **{R('play_to_pause')}**\n"
                f"» /pause {R('command')}"
            )
        except Exception as e:
            traceback.print_exc()
            await m.reply_text(f"🚫 **{R('error')}**\n\n`{e}`")
    else:
        await m.reply_text(f"❌ **{R('play_nothing')}**")


@Client.on_message(command(["skip", f"skip@{BOT_USERNAME}", "vskip"]) & other_filters)
@authorized_users_only
@check_blacklist()
async def skip(c: Client, m: Message):
    user_id = m.from_user.id
    chat_id = m.chat.id
    queue = await skip_current_song(chat_id)
    if queue == 0:
        await m.reply_text(f"❌ {R('play_nothing')}")
    elif queue == 1:
        await m.reply_text(f"» {R('queue_nothing')}")
    elif queue == 2:
        await m.reply_text(f"🗑️ {R('clear_queue')}\n\n"
                           f"{R('bot_leave')}")
    else:
        buttons = stream_markup(user_id)
        requester = f"[{m.from_user.first_name}](tg://user?id={m.from_user.id})"
        thumbnail = f"{IMG_5}"
        title = f"{queue[0]}"
        userid = m.from_user.id
        gcname = m.chat.title
        ctitle = await CHAT_TITLE(gcname)
        image = await thumb(thumbnail, title, userid, ctitle)
        await c.send_photo(
            chat_id,
            photo=image,
            reply_markup=InlineKeyboardMarkup(buttons),
            caption=f"⏭ {R('skip_to_next')}\n\n"
                    f"🗂 **{R('name')}** [{queue[0]}]({queue[1]})\n"
                    f"💭 **{R('chat')}** `{chat_id}`\n"
                    f"🧸 **{R('request')}** {requester}",
        )
        remove_if_exists(image)


@Client.on_message(
    command(["mute", f"mute@{BOT_USERNAME}", "vmute"]) & other_filters
)
@authorized_users_only
@check_blacklist()
async def mute(client, m: Message):
    chat_id = m.chat.id
    if chat_id in QUEUE:
        try:
            if not await is_music_playing(chat_id):
                return await m.reply_text(f"ℹ️ {R('play_muted')}")
            await calls.mute_stream(chat_id)
            await music_off(chat_id)
            await m.reply_text(
                f"🔇 **{R('play_mute')}**\n\n"
                f"• **{R('play_to_unmute')}**\n"
                f"» /unmute {R('command')}"
            )
        except Exception as e:
            traceback.print_exc()
            await m.reply_text(f"🚫 **{R('error')}**\n\n`{e}`")
    else:
        await m.reply_text(f"❌ **{R('play_nothing')}**")


@Client.on_message(
    command(["unmute", f"unmute@{BOT_USERNAME}", "vunmute"]) & other_filters
)
@authorized_users_only
@check_blacklist()
async def unmute(client, m: Message):
    chat_id = m.chat.id
    if chat_id in QUEUE:
        try:
            if await is_music_playing(chat_id):
                return await m.reply_text(f"ℹ️ {R('play_unmuted')}")
            await calls.unmute_stream(chat_id)
            await music_on(chat_id)
            await m.reply_text(
                f"🔊 **{R('play_unmute')}**\n\n"
                f"• **{R('play_to_mute')}**\n"
                f"» /mute {R('command')}"
            )
        except Exception as e:
            traceback.print_exc()
            await m.reply_text(f"🚫 **{R('error')}**\n\n`{e}`")
    else:
        await m.reply_text(f"❌ **{R('play_nothing')}**")


@Client.on_message(
    command(["volume", f"volume@{BOT_USERNAME}", "vol"]) & other_filters
)
@authorized_users_only
@check_blacklist()
@require_admin(permissions=["can_manage_voice_chats"], user_bot=True)
async def change_volume(c: Client, m: Message):
    if len(m.command) < 2:
        return await m.reply_text(f"{R('volume_help')}")
    range = m.command[1]
    chat_id = m.chat.id
    if chat_id in QUEUE:
        try:
            await calls.change_volume_call(chat_id, volume=int(range))
            await m.reply_text(
                f"✅ **{R('volume_set')}** `{range}`%"
            )
        except Exception as e:
            traceback.print_exc()
            await m.reply_text(f"🚫 **{R('error')}**\n\n`{e}`")
    else:
        await m.reply_text(f"❌ **{R('play_nothing')}**")


@Client.on_callback_query(filters.regex("set_pause"))
@check_blacklist()
@require_admin(permissions=["can_manage_voice_chats"])
async def cbpause(_, query: CallbackQuery):
    chat_id = query.message.chat.id
    if chat_id in QUEUE:
        try:
            if not await is_music_playing(chat_id):
                await query.answer(f"ℹ️ {R('play_paused')}", show_alert=True)
                return
            await calls.pause_stream(chat_id)
            await music_off(chat_id)
            await query.answer(f"⏸ {R('play_button_pause')}\n\n"
                               f"» {R('play_button_to_resume')}",
                               show_alert=True)
        except Exception as e:
            traceback.print_exc()
            await query.edit_message_text(f"🚫 **{R('error')}**\n\n`{e}`", reply_markup=close_mark)
    else:
        await query.answer(f"❌ {R('play_nothing')}", show_alert=True)


@Client.on_callback_query(filters.regex("set_resume"))
@check_blacklist()
@require_admin(permissions=["can_manage_voice_chats"])
async def cbresume(_, query: CallbackQuery):
    chat_id = query.message.chat.id
    if chat_id in QUEUE:
        try:
            if await is_music_playing(chat_id):
                await query.answer(f"ℹ️ {R('play_paused')}", show_alert=True)
                return
            await calls.resume_stream(chat_id)
            await music_on(chat_id)
            await query.answer(f"⏸ {R('play_button_pause')}\n\n"
                               f"» {R('play_button_to_resume')}",
                               show_alert=True)
        except Exception as e:
            traceback.print_exc()
            await query.edit_message_text(f"🚫 **{R('error')}**\n\n`{e}`", reply_markup=close_mark)
    else:
        await query.answer(f"❌ {R('play_nothing')}", show_alert=True)


@Client.on_callback_query(filters.regex("set_stop"))
@check_blacklist()
@require_admin(permissions=["can_manage_voice_chats"])
async def cbstop(_, query: CallbackQuery):
    chat_id = query.message.chat.id
    if chat_id in QUEUE:
        try:
            await calls.leave_group_call(chat_id)
            await remove_active_chat(chat_id)
            clear_queue(chat_id)
            await query.edit_message_text(f"✅ **{R('play_button_ended')}**", reply_markup=close_mark)
        except Exception as e:
            traceback.print_exc()
            await query.edit_message_text(f"🚫 **{R('error')}**\n\n`{e}`", reply_markup=close_mark)
    else:
        await query.answer(f"❌ {R('play_nothing')}", show_alert=True)


@Client.on_callback_query(filters.regex("set_mute"))
@check_blacklist()
@require_admin(permissions=["can_manage_voice_chats"])
async def cbmute(_, query: CallbackQuery):
    chat_id = query.message.chat.id
    if chat_id in QUEUE:
        try:
            if not await is_music_playing(chat_id):
                await query.answer(f"ℹ️ {R('play_button_mute')}", show_alert=True)
                return
            await calls.mute_stream(chat_id)
            await music_off(chat_id)
            await query.answer(f"🔇 {R('play_button_muted')}\n\n"
                               f"» {R('play_button_to_unmute')}",
                               show_alert=True)
        except Exception as e:
            traceback.print_exc()
            await query.edit_message_text(f"🚫 **{R('error')}**\n\n`{e}`", reply_markup=close_mark)
    else:
        await query.answer(f"❌ {R('play_nothing')}", show_alert=True)


@Client.on_callback_query(filters.regex("set_unmute"))
@check_blacklist()
@require_admin(permissions=["can_manage_voice_chats"])
async def cbunmute(_, query: CallbackQuery):
    chat_id = query.message.chat.id
    if chat_id in QUEUE:
        try:
            if await is_music_playing(chat_id):
                await query.answer(f"ℹ️ {R('play_button_unmute')}", show_alert=True)
                return
            await calls.unmute_stream(chat_id)
            await music_on(chat_id)
            await query.answer(f"🔊 {R('play_button_unmuted')}\n\n"
                               f"» {R('play_button_to_mute')}",
                               show_alert=True)
        except Exception as e:
            traceback.print_exc()
            await query.edit_message_text(f"🚫 **{R('error')}**\n\n`{e}`", reply_markup=close_mark)
    else:
        await query.answer(f"❌ {R('play_nothing')}", show_alert=True)


@Client.on_callback_query(filters.regex("set_skip"))
@check_blacklist()
@require_admin(permissions=["can_manage_voice_chats"])
async def cbskip(_, query: CallbackQuery):
    chat_id = query.message.chat.id
    user_id = query.from_user.id
    queue = await skip_current_song(chat_id)
    if queue == 0:
        await query.answer(f"❌ {R('play_nothing')}", show_alert=True)
    elif queue == 1:
        await query.answer(f"» {R('queue_nothing')}", show_alert=True)
    elif queue == 2:
        await query.answer(f"🗑️ {R('clear_queue')}\n\n"
                           f"{R('bot_leave')}",
                           show_alert=True)
    else:
        await query.answer(f"{R('play_button_skip')}")
        await query.message.delete()
        buttons = stream_markup(user_id)
        requester = f"[{query.from_user.first_name}](tg://user?id={query.from_user.id})"
        thumbnail = f"{IMG_5}"
        title = f"{queue[0]}"
        userid = query.from_user.id
        gcname = query.message.chat.title
        ctitle = await CHAT_TITLE(gcname)
        image = await thumb(thumbnail, title, userid, ctitle)
        await _.send_photo(
            chat_id,
            photo=image,
            reply_markup=InlineKeyboardMarkup(buttons),
            caption=f"⏭ {R('skip_to_next')}\n\n"
                    f"🗂 **{R('name')}** [{queue[0]}]({queue[1]})\n"
                    f"💭 **{R('chat')}** `{chat_id}`\n"
                    f"🧸 **{R('request')}** {requester}",
        )
        remove_if_exists(image)
