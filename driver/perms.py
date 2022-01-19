import asyncio
from driver.veez import bot
from pyrogram.types import Message

async def member_permissions(chat_id: int, user_id: int):
    perms = []
    member = await bot.get_chat_member(chat_id, user_id)
    if member.can_manage_voice_chats:
        perms.append("can_manage_voice_chats")
    return perms
