""" chat utilities """

from functools import wraps

from driver.veez import bot
from config import SUDO_USERS
from pyrogram.types import Message
from program.admins import member_permissions
from pyrogram.errors.exceptions.forbidden_403 import ChatWriteForbidden


async def authorised(message):
    chatID = message.chat.id
    return 0


async def unauthorised(message: Message):
    chatID = message.chat.id
    text = (
        "You're missing admin rights to use this command."
        + f"\n\n» ❌ can_manage_voice_chats"
    )
    try:
        await message.reply_text(text)
    except ChatWriteForbidden:
        await bot.leave_chat(chatID)
    return 1

  
async def adminsOnly(permission, message):
    chatID = message.chat.id
    if not message.from_user:
        if message.sender_chat:
            return await authorised(message)
        return await unauthorised(message)
    userID = message.from_user.id
    permissions = await member_permissions(chatID, userID)
    if userID not in SUDO_USERS and permission not in permissions:
        return await unauthorised(message)
    return await authorised(message)
