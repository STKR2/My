from io import BytesIO
from pyrogram.types import Message
from pyrogram import Client, filters

from config import BOT_USERNAME
from driver.filters import command
from driver.decorators import sudo_users_only, get_arg
from driver.database.data_sql import chatdata, del_chat


@Client.on_message(
    command(["broadcast", f"broadcast@{BOT_USERNAME}"]) & filters.private & ~filters.edited
)
@sudo_users_only
async def broadcast(client: Client, message: Message):
    to_send = get_arg(message)
    success = 0
    failed = 0
    for chat in chatdata()():
        try:
            await client.send_message(
                str(chat),
                to_send
            )
            success += 1
        except BaseException:
            failed += 1
            del_chat(str(chat))
    await message.reply(
        f"Message sent to {success} chat(s). {failed} chat(s) failed recieve message"
    )


@Client.on_message(
    command(["chatlist", f"chatlist@{BOT_USERNAME}"]) & filters.private & ~filters.edited
)
@sudo_users_only
async def chatlist(client, message):
    all_chats = chatdata()
    chats = [i for i in all_chats if str(i).startswith("-")]
    chatfile = "Chat List.\n0. Group ID | Members | Invite Link\n"
    P = 1
    for chat in chats:
        try:
            link = await client.export_chat_invite_link(int(chat))
        except BaseException:
            link = "Null"
        try:
            members = await client.get_chat_members_count(int(chat))
        except BaseException:
            members = "Null"
        try:
            chatfile += f"{P}. {chat} | {members} | {link}\n"
            P += 1
        except BaseException:
            pass
    with BytesIO(str.encode(chatfile)) as output:
        output.name = "chatlist.txt"
        await message.reply_document(document=output, disable_notification=True)
