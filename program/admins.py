from cache.admins import admins
from driver.veez import call_py, bot
from pyrogram import Client, filters
from driver.design.thumbnail import thumb
from driver.design.chatname import CHAT_TITLE
from driver.queues import QUEUE, clear_queue
from driver.filters import command, other_filters
from driver.decorators import authorized_users_only
from driver.utils import skip_current_song, skip_item
from driver.database.dbpunish import is_gbanned_user

from program.utils.inline import (
    stream_markup,
    close_mark,
    back_mark,
)
from config import BOT_USERNAME, GROUP_SUPPORT, IMG_5, UPDATES_CHANNEL
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)


@Client.on_message(command(["reload", f"reload@{BOT_USERNAME}"]) & other_filters)
@authorized_users_only
async def update_admin(client, message: Message):
    global admins
    new_admins = []
    user_id = message.from_user.id
    if await is_gbanned_user(user_id):
        await message.reply_text("❗️ **You've blocked from using this bot!**")
        return
    new_ads = await client.get_chat_members(message.chat.id, filter="administrators")
    for u in new_ads:
        new_admins.append(u.user.id)
    admins[message.chat.id] = new_admins
    await message.reply_text(
        "✅ Bot **reloaded correctly !**\n✅ **Admin list** has **updated !**"
    )


@Client.on_message(command(["skip", f"skip@{BOT_USERNAME}", "vskip"]) & other_filters)
@authorized_users_only
async def skip(c: Client, m: Message):
    await m.delete()
    user_id = m.from_user.id
    chat_id = m.chat.id
    user_xd = f"[{m.from_user.first_name}](tg://user?id={m.from_user.id})"
    if await is_gbanned_user(user_id):
        await message.reply_text(f"❗️ {user_xd} **You've blocked from using this bot!**")
        return
    if len(m.command) < 2:
        op = await skip_current_song(chat_id)
        if op == 0:
            await c.send_message(chat_id, "❌ nothing is currently playing")
        elif op == 1:
            await c.send_message(chat_id, "» There's no more music in queue to skip, userbot leaving video chat.")
        elif op == 2:
            await c.send_message(chat_id, "🗑️ Clearing the **Queues**\n\n**• userbot** leaving video chat.")
        else:
            buttons = stream_markup(user_id)
            requester = f"[{m.from_user.first_name}](tg://user?id={m.from_user.id})"
            thumbnail = f"{IMG_5}"
            title = f"{op[0]}"
            userid = m.from_user.id
            gcname = m.chat.title
            ctitle = await CHAT_TITLE(gcname)
            image = await thumb(thumbnail, title, userid, ctitle)
            await c.send_photo(
                chat_id,
                photo=image,
                reply_markup=InlineKeyboardMarkup(buttons),
                caption=f"⏭ **Skipped** to the next track.\n\n🗂 **Name:** [{op[0]}]({op[1]})\n💭 **Chat:** `{chat_id}`\n🧸 **Request by:** {requester}",
            )
    else:
        skip = m.text.split(None, 1)[1]
        OP = "🗑 **removed song from queue:**"
        if chat_id in QUEUE:
            items = [int(x) for x in skip.split(" ") if x.isdigit()]
            items.sort(reverse=True)
            for x in items:
                if x == 0:
                    pass
                else:
                    hm = await skip_item(chat_id, x)
                    if hm == 0:
                        pass
                    else:
                        OP = OP + "\n" + f"**#{x}** - {hm}"
            await m.reply(OP)


@Client.on_message(
    command(["stop", f"stop@{BOT_USERNAME}", "end", f"end@{BOT_USERNAME}", "vstop"])
    & other_filters
)
@authorized_users_only
async def stop(client, m: Message):
    user_id = m.from_user.id
    if await is_gbanned_user(user_id):
        await message.reply_text("❗️ **You've blocked from using this bot!**")
        return
    chat_id = m.chat.id
    if chat_id in QUEUE:
        try:
            await call_py.leave_group_call(chat_id)
            clear_queue(chat_id)
            await m.reply("✅ The userbot has disconnected from the video chat.")
        except Exception as e:
            await m.reply(f"🚫 **error:**\n\n`{e}`")
    else:
        await m.reply("❌ **nothing is streaming**")


@Client.on_message(
    command(["pause", f"pause@{BOT_USERNAME}", "vpause"]) & other_filters
)
@authorized_users_only
async def pause(client, m: Message):
    user_id = m.from_user.id
    if await is_gbanned_user(user_id):
        await message.reply_text("❗️ **You've blocked from using this bot!**")
        return
    chat_id = m.chat.id
    if chat_id in QUEUE:
        try:
            await call_py.pause_stream(chat_id)
            await m.reply(
                "⏸ **Track paused.**\n\n• **To resume the stream, use the**\n» /resume command."
            )
        except Exception as e:
            await m.reply(f"🚫 **error:**\n\n`{e}`")
    else:
        await m.reply("❌ **nothing is streaming**")


@Client.on_message(
    command(["resume", f"resume@{BOT_USERNAME}", "vresume"]) & other_filters
)
@authorized_users_only
async def resume(client, m: Message):
    user_id = m.from_user.id
    if await is_gbanned_user(user_id):
        await message.reply_text("❗️ **You've blocked from using this bot!**")
        return
    chat_id = m.chat.id
    if chat_id in QUEUE:
        try:
            await call_py.resume_stream(chat_id)
            await m.reply(
                "▶️ **Track resumed.**\n\n• **To pause the stream, use the**\n» /pause command."
            )
        except Exception as e:
            await m.reply(f"🚫 **error:**\n\n`{e}`")
    else:
        await m.reply("❌ **nothing is streaming**")


@Client.on_message(
    command(["mute", f"mute@{BOT_USERNAME}", "vmute"]) & other_filters
)
@authorized_users_only
async def mute(client, m: Message):
    user_id = m.from_user.id
    if await is_gbanned_user(user_id):
        await message.reply_text("❗️ **You've blocked from using this bot!**")
        return
    chat_id = m.chat.id
    if chat_id in QUEUE:
        try:
            await call_py.mute_stream(chat_id)
            await m.reply(
                "🔇 **Userbot muted.**\n\n• **To unmute the userbot, use the**\n» /unmute command."
            )
        except Exception as e:
            await m.reply(f"🚫 **error:**\n\n`{e}`")
    else:
        await m.reply("❌ **nothing is streaming**")


@Client.on_message(
    command(["unmute", f"unmute@{BOT_USERNAME}", "vunmute"]) & other_filters
)
@authorized_users_only
async def unmute(client, m: Message):
    user_id = m.from_user.id
    if await is_gbanned_user(user_id):
        await message.reply_text("❗️ **You've blocked from using this bot!**")
        return
    chat_id = m.chat.id
    if chat_id in QUEUE:
        try:
            await call_py.unmute_stream(chat_id)
            await m.reply(
                "🔊 **Userbot unmuted.**\n\n• **To mute the userbot, use the**\n» /mute command."
            )
        except Exception as e:
            await m.reply(f"🚫 **error:**\n\n`{e}`")
    else:
        await m.reply("❌ **nothing is streaming**")


@Client.on_callback_query(filters.regex("set_pause"))
async def cbpause(_, query: CallbackQuery):
    user_id = query.from_user.id
    if await is_gbanned_user(user_id):
        await query.answer("❗️ You've blocked from using this bot!", show_alert=True)
        return
    a = await _.get_chat_member(query.message.chat.id, query.from_user.id)
    if not a.can_manage_voice_chats:
        return await query.answer("💡 Only admin with manage video chat permission that can tap this button !", show_alert=True)
    chat_id = query.message.chat.id
    if chat_id in QUEUE:
        try:
            await call_py.pause_stream(chat_id)
            await query.answer("streaming paused")
            await query.edit_message_text(
                "⏸ the streaming has paused", reply_markup=back_mark
            )
        except Exception as e:
            await query.edit_message_text(f"🚫 **error:**\n\n`{e}`", reply_markup=close_mark)
    else:
        await query.answer("❌ nothing is currently streaming", show_alert=True)


@Client.on_callback_query(filters.regex("set_resume"))
async def cbresume(_, query: CallbackQuery):
    user_id = query.from_user.id
    if await is_gbanned_user(user_id):
        await query.answer("❗️ You've blocked from using this bot!", show_alert=True)
        return
    a = await _.get_chat_member(query.message.chat.id, query.from_user.id)
    if not a.can_manage_voice_chats:
        return await query.answer("💡 Only admin with manage video chat permission that can tap this button !", show_alert=True)
    chat_id = query.message.chat.id
    if chat_id in QUEUE:
        try:
            await call_py.resume_stream(chat_id)
            await query.answer("streaming resumed")
            await query.edit_message_text(
                "▶️ the streaming has resumed", reply_markup=back_mark
            )
        except Exception as e:
            await query.edit_message_text(f"🚫 **error:**\n\n`{e}`", reply_markup=close_mark)
    else:
        await query.answer("❌ nothing is currently streaming", show_alert=True)


@Client.on_callback_query(filters.regex("set_stop"))
async def cbstop(_, query: CallbackQuery):
    user_id = query.from_user.id
    if await is_gbanned_user(user_id):
        await query.answer("❗️ You've blocked from using this bot!", show_alert=True)
        return
    a = await _.get_chat_member(query.message.chat.id, query.from_user.id)
    if not a.can_manage_voice_chats:
        return await query.answer("💡 Only admin with manage video chat permission that can tap this button !", show_alert=True)
    chat_id = query.message.chat.id
    if chat_id in QUEUE:
        try:
            await call_py.leave_group_call(chat_id)
            clear_queue(chat_id)
            await query.edit_message_text("✅ **this streaming has ended**", reply_markup=close_mark)
        except Exception as e:
            await query.edit_message_text(f"🚫 **error:**\n\n`{e}`", reply_markup=close_mark)
    else:
        await query.answer("❌ nothing is currently streaming", show_alert=True)


@Client.on_callback_query(filters.regex("set_mute"))
async def cbmute(_, query: CallbackQuery):
    user_id = query.from_user.id
    if await is_gbanned_user(user_id):
        await query.answer("❗️ You've blocked from using this bot!", show_alert=True)
        return
    a = await _.get_chat_member(query.message.chat.id, query.from_user.id)
    if not a.can_manage_voice_chats:
        return await query.answer("💡 Only admin with manage video chat permission that can tap this button !", show_alert=True)
    chat_id = query.message.chat.id
    if chat_id in QUEUE:
        try:
            await call_py.mute_stream(chat_id)
            await query.answer("streaming muted")
            await query.edit_message_text(
                "🔇 userbot succesfully muted", reply_markup=back_mark
            )
        except Exception as e:
            await query.edit_message_text(f"🚫 **error:**\n\n`{e}`", reply_markup=close_mark)
    else:
        await query.answer("❌ nothing is currently streaming", show_alert=True)


@Client.on_callback_query(filters.regex("set_unmute"))
async def cbunmute(_, query: CallbackQuery):
    user_id = query.from_user.id
    if await is_gbanned_user(user_id):
        await query.answer("❗️ You've blocked from using this bot!", show_alert=True)
        return
    a = await _.get_chat_member(query.message.chat.id, query.from_user.id)
    if not a.can_manage_voice_chats:
        return await query.answer("💡 Only admin with manage video chat permission that can tap this button !", show_alert=True)
    chat_id = query.message.chat.id
    if chat_id in QUEUE:
        try:
            await call_py.unmute_stream(chat_id)
            await query.answer("streaming unmuted")
            await query.edit_message_text(
                "🔊 userbot succesfully unmuted", reply_markup=back_mark
            )
        except Exception as e:
            await query.edit_message_text(f"🚫 **error:**\n\n`{e}`", reply_markup=close_mark)
    else:
        await query.answer("❌ nothing is currently streaming", show_alert=True)


@Client.on_message(
    command(["volume", f"volume@{BOT_USERNAME}", "vol"]) & other_filters
)
@authorized_users_only
async def change_volume(client, m: Message):
    user_id = m.from_user.id
    if await is_gbanned_user(user_id):
        await message.reply_text("❗️ **You've blocked from using this bot!**")
        return
    range = m.command[1]
    chat_id = m.chat.id
    if chat_id in QUEUE:
        try:
            await call_py.change_volume_call(chat_id, volume=int(range))
            await m.reply(
                f"✅ **volume set to** `{range}`%"
            )
        except Exception as e:
            await m.reply(f"🚫 **error:**\n\n`{e}`")
    else:
        await m.reply("❌ **nothing in streaming**")
