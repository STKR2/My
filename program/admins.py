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
from driver.decorators import authorized_users_only, check_blacklist
from driver.utils import skip_current_song, skip_item, remove_if_exists
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


@Client.on_message(command(["تحديث", f"عيد"]) & other_filters)
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
        "✅ تم اعادة **تشغيل البوت** !\n✅ وتم **تحديث** قائمة **المشرفين.**"
    )


@Client.on_message(
    command(["كافي", f"اوكف", "ك", f"ايقاف", "انهاء"])
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
            await m.reply_text(" 🦴 اެبشࢪ يحݪۅ تَم ۅكَفت اެݪاغِنية بَعد ؟..")
        except Exception as e:
            traceback.print_exc()
            await m.reply_text(f"🚫 **error:**\n\n`{e}`")
    else:
        await m.reply_text("معݪش ، ماެفي شي مشتغݪ ياެعيني🌵.")


@Client.on_message(
    command(["توقف", f"pause@{BOT_USERNAME}", "vpause"]) & other_filters
)
@authorized_users_only
@check_blacklist()
async def pause(client, m: Message):
    chat_id = m.chat.id
    if chat_id in QUEUE:
        try:
            if not await is_music_playing(chat_id):
                return await m.reply_text("ℹ️ الموسيقى متوقفة مؤقتًا بالفعل.")
            await calls.pause_stream(chat_id)
            await music_off(chat_id)
            await m.reply_text(
                "⏸ **تم إيقاف المسار مؤقتًا.**\n\n• **لاستمرار الاغنية اكتب**\n»-›  .استمرار"
            )
        except Exception as e:
            traceback.print_exc()
            await m.reply_text(f"🚫 **error:**\n\n`{e}`")
    else:
        await m.reply_text("معݪش ، ماެفي شي مشتغݪ ياެعيني🌵.")


@Client.on_message(
    command(["استمرار", f"resume@{BOT_USERNAME}", "vresume"]) & other_filters
)
@authorized_users_only
@check_blacklist()
async def resume(client, m: Message):
    chat_id = m.chat.id
    if chat_id in QUEUE:
        try:
            if await is_music_playing(chat_id):
                return await m.reply_text("ℹ️ تم تشغيل الموسيقى بالفعل.")
            await calls.resume_stream(chat_id)
            await music_on(chat_id)
            await m.reply_text(
                "▶️ **ابشر تم الإستمرار.**\n\n• **لايقاف الأغنية اكتب**\n» .توقف"
            )
        except Exception as e:
            traceback.print_exc()
            await m.reply_text(f"🚫 **error:**\n\n`{e}`")
    else:
        await m.reply_text("معݪش ، ماެفي شي مشتغݪ ياެعيني🌵.")


@Client.on_message(command(["تخطي", f"تخ", "التالي"]) & other_filters)
@authorized_users_only
@check_blacklist()
async def skip(c: Client, m: Message):
    user_id = m.from_user.id
    chat_id = m.chat.id
    queue = await skip_current_song(chat_id)
    if queue == 0:
        await m.reply_text("معݪش ، ماެفي شي مشتغݪ ياެعيني🌵.")
    elif queue == 1:
        await m.reply_text(" معݪش ، ماެفي شي مشتغݪ ياެعيني🌵..")
    elif queue == 2:
        await m.reply_text("🗑️ تم مسح**الانتضار**\n\n» **والمساعد** غادر الدردشة الصوتية.")
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
            caption=f"⏭ **اެبشࢪ يحݪۅ** تم اެݪتخطي اެݪى اݪمساࢪ اެݪتالي.\n\n❤️‍🔥 **اެݪاެسم:** [{queue[0]}]({queue[1]})\n❤️‍🔥 **اެݪدࢪدشةه:** `{chat_id}`\n🦴 **طݪب اެݪحݪۅ:** {requester}",
        )
        remove_if_exists(image)


@Client.on_message(
    command(["كتم", f"mute@{BOT_USERNAME}", "vmute"]) & other_filters
)
@authorized_users_only
@check_blacklist()
async def mute(client, m: Message):
    chat_id = m.chat.id
    if chat_id in QUEUE:
        try:
            if not await is_music_playing(chat_id):
                return await m.reply_text("ℹ️ تم كتمة بالفعل.")
            await calls.mute_stream(chat_id)
            await music_off(chat_id)
            await m.reply_text(
                "🔇 **تم كتم صوت المساعد.**\n\n• **لإلغاء كتم الصوت اكتب**\n» .بلش"
            )
        except Exception as e:
            traceback.print_exc()
            await m.reply_text(f"🚫 **error:**\n\n`{e}`")
    else:
        await m.reply_text("معݪش ، ماެفي شي مشتغݪ ياެعيني🌵.")


@Client.on_message(
    command(["بلش", f"unmute@{BOT_USERNAME}", "vunmute"]) & other_filters
)
@authorized_users_only
@check_blacklist()
async def unmute(client, m: Message):
    chat_id = m.chat.id
    if chat_id in QUEUE:
        try:
            if await is_music_playing(chat_id):
                return await m.reply_text("ℹ️ جاي يغني منزمان .")
            await calls.unmute_stream(chat_id)
            await music_on(chat_id)
            await m.reply_text(
                "🔊 **تم الغاء الكتم.**\n\n• **لكتمة مره اخرى اكتب**\n» .كتم"
            )
        except Exception as e:
            traceback.print_exc()
            await m.reply_text(f"🚫 **error:**\n\n`{e}`")
    else:
        await m.reply_text("معݪش ، ماެفي شي مشتغݪ ياެعيني🌵.")


@Client.on_message(
    command(["ضبط", f"اضبط", "vol"]) & other_filters
)
@authorized_users_only
@check_blacklist()
async def change_volume(c: Client, m: Message):
    if len(m.command) < 2:
        return await m.reply_text("الاستخدام: `.اضبط` (`0-200`)")
    a = await c.get_chat_member(m.chat.id, me_user.id)
    if not a.can_manage_voice_chats:
        return await m.reply_text(
            " 👍🏻لاستخدام هذه الامر ، عليك رفع حساب المساعد : بصلاحية الدردشة الصوتية"
        )
    range = m.command[1]
    chat_id = m.chat.id
    if chat_id in QUEUE:
        try:
            await calls.change_volume_call(chat_id, volume=int(range))
            await m.reply_text(
                f"-›  **تم وسويت الصوت** `{range}`%"
            )
        except Exception as e:
            traceback.print_exc()
            await m.reply_text(f"🚫 **error:**\n\n`{e}`")
    else:
        await m.reply_text("معݪش ، ماެفي شي مشتغݪ ياެعيني🌵.")


@Client.on_callback_query(filters.regex("set_pause"))
@check_blacklist()
async def cbpause(_, query: CallbackQuery):
    a = await _.get_chat_member(query.message.chat.id, query.from_user.id)
    if not a.can_manage_voice_chats:
        return await query.answer("💡 وخر ايدك لاتبعبص محد يكدر يدوس هنا بس الي عنده صلاحية المكالمات !", show_alert=True)
    chat_id = query.message.chat.id
    if chat_id in QUEUE:
        try:
            if not await is_music_playing(chat_id):
                await query.answer("ℹ️ الموسيقى متوقفة مؤقتًا بالفعل.", show_alert=True)
                return
            await calls.pause_stream(chat_id)
            await music_off(chat_id)
            await query.answer("⏸ توقفت الاغنية مؤقتًا !\n\n-›  لتشغيلها مره اخرى إنقر على زر استمرار", show_alert=True)
        except Exception as e:
            traceback.print_exc()
            await query.edit_message_text(f"🚫 **error:**\n\n`{e}`", reply_markup=close_mark)
    else:
        await query.answer("معݪش ، ماެفي شي مشتغݪ ياެعيني🌵.", show_alert=True)


@Client.on_callback_query(filters.regex("set_resume"))
@check_blacklist()
async def cbresume(_, query: CallbackQuery):
    a = await _.get_chat_member(query.message.chat.id, query.from_user.id)
    if not a.can_manage_voice_chats:
        return await query.answer("💡 وخر ايدك لاتبعبص محد يكدر يدوس هنا بس الي عنده صلاحية المكالمات !", show_alert=True)
    chat_id = query.message.chat.id
    if chat_id in QUEUE:
        try:
            if await is_music_playing(chat_id):
                await query.answer("ℹ️ تم تشغيل الاغنية مرة اخرى بالفعل.", show_alert=True)
                return
            await calls.resume_stream(chat_id)
            await music_on(chat_id)
            await query.answer("▶️ تم التشغيل !\n\n» لإيقافها مره اخرى انقر على زر الايقاف ", show_alert=True)
        except Exception as e:
            traceback.print_exc()
            await query.edit_message_text(f"🚫 **error:**\n\n`{e}`", reply_markup=close_mark)
    else:
        await query.answer("معݪش ، ماެفي شي مشتغݪ ياެعيني🌵.", show_alert=True)


@Client.on_callback_query(filters.regex("set_stop"))
@check_blacklist()
async def cbstop(_, query: CallbackQuery):
    a = await _.get_chat_member(query.message.chat.id, query.from_user.id)
    if not a.can_manage_voice_chats:
        return await query.answer("💡 وخر ايدك لاتبعبص محد يكدر يدوس هنا بس الي عنده صلاحية المكالمات !", show_alert=True)
    chat_id = query.message.chat.id
    if chat_id in QUEUE:
        try:
            await calls.leave_group_call(chat_id)
            await remove_active_chat(chat_id)
            clear_queue(chat_id)
            await query.edit_message_text("✅ ابشر تم نهيت كلشي.", reply_markup=close_mark)
        except Exception as e:
            traceback.print_exc()
            await query.edit_message_text(f"🚫 **error:**\n\n`{e}`", reply_markup=close_mark)
    else:
        await query.answer("معݪش ، ماެفي شي مشتغݪ ياެعيني🌵.", show_alert=True)


@Client.on_callback_query(filters.regex("set_mute"))
@check_blacklist()
async def cbmute(_, query: CallbackQuery):
    a = await _.get_chat_member(query.message.chat.id, query.from_user.id)
    if not a.can_manage_voice_chats:
        return await query.answer("💡 وخر ايدك لاتبعبص محد يكدر يدوس هنا بس الي عنده صلاحية المكالمات !", show_alert=True)
    chat_id = query.message.chat.id
    if chat_id in QUEUE:
        try:
            if not await is_music_playing(chat_id):
                await query.answer("ℹ️ تم كتم صوت المساعد بالفعل.", show_alert=True)
                return
            await calls.mute_stream(chat_id)
            await music_off(chat_id)
            await query.answer("🔇 تم كتم صوت المساعد !\n\n-›  لتشغيلة مره اخرى انقر على زر الاستئناف", show_alert=True)
        except Exception as e:
            traceback.print_exc()
            await query.edit_message_text(f"🚫 **error:**\n\n`{e}`", reply_markup=close_mark)
    else:
        await query.answer("معݪش ، ماެفي شي مشتغݪ ياެعيني🌵.", show_alert=True)


@Client.on_callback_query(filters.regex("set_unmute"))
@check_blacklist()
async def cbunmute(_, query: CallbackQuery):
    a = await _.get_chat_member(query.message.chat.id, query.from_user.id)
    if not a.can_manage_voice_chats:
        return await query.answer("💡 وخر ايدك لاتبعبص محد يكدر يدوس هنا بس الي عنده صلاحية المكالمات !", show_alert=True)
    chat_id = query.message.chat.id
    if chat_id in QUEUE:
        try:
            if await is_music_playing(chat_id):
                await query.answer("ℹ️ تم تشغيل الاغنية بالفعل.", show_alert=True)
                return
            await calls.unmute_stream(chat_id)
            await music_on(chat_id)
            await query.answer("🔊 تم الغاء كتم صوت المساعد !\n\n» لكتم المساعد انقر على زر كتم", show_alert=True)
        except Exception as e:
            traceback.print_exc()
            await query.edit_message_text(f"🚫 **error:**\n\n`{e}`", reply_markup=close_mark)
    else:
        await query.answer("معݪش ، ماެفي شي مشتغݪ ياެعيني🌵.", show_alert=True)


@Client.on_callback_query(filters.regex("set_skip"))
@check_blacklist()
async def cbskip(_, query: CallbackQuery):
    a = await _.get_chat_member(query.message.chat.id, query.from_user.id)
    if not a.can_manage_voice_chats:
        return await query.answer("💡 وخر ايدك لاتبعبص محد يكدر يدوس هنا بس الي عنده صلاحية المكالمات !", show_alert=True)
    chat_id = query.message.chat.id
    user_id = query.from_user.id
    queue = await skip_current_song(chat_id)
    if queue == 0:
        await query.answer("معݪش ، ماެفي شي مشتغݪ ياެعيني🌵.", show_alert=True)
    elif queue == 1:
        await query.answer("معݪش ، ماެفي شي مشتغݪ ياެعيني🌵.", show_alert=True)
    elif queue == 2:
        await query.answer("🗑️ تم مسح **الانتضار**\n\n» **والمساعد** غادر الدردشة الصوتية.", show_alert=True)
    else:
        await query.answer("ابشر جاري الانتقال الى الاغنية الثانية..")
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
            caption=f"⏭ **اެبشࢪ يحݪۅ** تم اެݪتخطي اެݪى اݪمساࢪ اެݪتالي.\n\n❤️‍🔥 **Name:** [{queue[0]}]({queue[1]})\n❤️‍🔥 **Chat:** `{chat_id}`\n🦴 **طݪب اެݪحݪۅ:** {requester}",
        )
        remove_if_exists(image)
