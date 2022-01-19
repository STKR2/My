""" chat utilities """

import asyncio
from functools import wraps
from driver.veez import bot
from config import SUDO_USERS
from pyrogram.types import Message
from driver.perms import member_permissions
from pyrogram.errors.exceptions.forbidden_403 import ChatWriteForbidden


async def authorised(m: Message):
    chatID = message.chat.id
    return 0


async def unauthorised(m: Message):
    chatID = m.chat.id
    text = (
        "You're missing admin rights to use this command."
        + f"\n\n» ❌ can_manage_voice_chats"
    )
    try:
        await m.reply_text(text)
    except ChatWriteForbidden:
        await bot.leave_chat(chatID)
    return 1

  
async def adminsOnly(permission, m: Message):
    chatID = m.chat.id
    if not m.from_user:
        if m.sender_chat:
            return await authorised(m)
        return await unauthorised(m)
    userID = m.from_user.id
    permissions = await member_permissions(chatID, userID)
    if userID not in SUDO_USERS and permission not in permissions:
        return await unauthorised(m)
    return await authorised(m)
