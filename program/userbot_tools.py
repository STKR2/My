import asyncio

from config import BOT_USERNAME, SUDO_USERS

from driver.core import user
from driver.filters import command, other_filters
from driver.database.dbchat import remove_served_chat
from driver.database.dbqueue import remove_active_chat
from driver.database.dbpunish import is_gbanned_user
from driver.decorators import authorized_users_only, bot_creator

from pyrogram.types import Message
from pyrogram import Client, filters
from pyrogram.errors import UserAlreadyParticipant, UserNotParticipant



@Client.on_message(
    command(["userbotjoin", f"userbotjoin@{BOT_USERNAME}"]) & other_filters
)
@authorized_users_only
async def join_chat(c: Client, m: Message):
    chat_id = m.chat.id
    user_id = m.from_user.id
    if await is_gbanned_user(user_id):
        await m.reply_text("❗️ **You've blocked from using this bot!**")
        return
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
        return await user.send_message(chat_id, "✅ userbot joined chat")
    except UserAlreadyParticipant:
        return await user.send_message(chat_id, "✅ userbot already in chat")


@Client.on_message(
    command(["userbotleave", f"userbotleave@{BOT_USERNAME}"]) & other_filters
)
@authorized_users_only
async def leave_chat(_, m: Message):
    chat_id = m.chat.id
    user_id = m.from_user.id
    if await is_gbanned_user(user_id):
        await m.reply_text("❗️ **You've blocked from using this bot!**")
        return
    try:
        await user.leave_chat(chat_id)
        await remove_active_chat(chat_id)
        return await _.send_message(
            chat_id,
            "✅ userbot leaved chat",
        )
    except UserNotParticipant:
        return await _.send_message(
            chat_id,
            "❌ userbot already leave chat",
        )


@Client.on_message(command(["leaveall", f"leaveall@{BOT_USERNAME}"]))
@bot_creator
async def leave_all(client, message):
    if message.from_user.id not in SUDO_USERS:
        return

    left = 0
    failed = 0
    
    msg = await message.reply("🔄 Userbot leaving all Group !")
    async for dialog in user.iter_dialogs():
        try:
            await user.leave_chat(dialog.chat.id)
            await remove_active_chat(dialog.chat.id)
            left += 1
            await msg.edit(
                f"Userbot leaving all Group...\n\nLeft: {left} chats.\nFailed: {failed} chats."
            )
        except BaseException:
            failed += 1
            await msg.edit(
                f"Userbot leaving...\n\nLeft: {left} chats.\nFailed: {failed} chats."
            )
        await asyncio.sleep(0.7)
    await msg.delete()
    await client.send_message(
        message.chat.id, f"✅ Left from: {left} chats.\n❌ Failed in: {failed} chats."
    )


@Client.on_message(filters.left_chat_member)
async def bot_kicked(c: Client, m: Message):
    bot_id = (await c.get_me()).id
    chat_id = m.chat.id
    left_member = m.left_chat_member
    if left_member.id == bot_id:
        await user.leave_chat(chat_id)
        await remove_served_chat(chat_id)
        await remove_active_chat(chat_id)
