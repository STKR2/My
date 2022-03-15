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


from driver.core import me_bot, me_user
from driver.queues import QUEUE
from driver.decorators import check_blacklist, require_admin
from driver.utils import R
from program.utils.inline import menu_markup, stream_markup

from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from config import (
    BOT_USERNAME,
    GROUP_SUPPORT,
    OWNER_USERNAME,
    UPDATES_CHANNEL,
    SUDO_USERS,
    OWNER_ID,
)


@Client.on_callback_query(filters.regex("home_start"))
@check_blacklist()
async def start_set(_, query: CallbackQuery):
    await query.answer(R("home_start_notice"))
    await query.edit_message_text(
        R("home_start").format(query.message.chat.first_name,
                               query.message.chat.id,
                               me_bot.first_name,
                               me_bot.username),
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(f"➕ {R('add_me_to_group')} ➕", url=f"https://t.me/{me_bot.username}?startgroup=true")
                ],[
                    InlineKeyboardButton(f"❓ {R('basic_guide')}", callback_data="user_guide")
                ],[
                    InlineKeyboardButton(f"📚 {R('commands')}", callback_data="command_list"),
                    InlineKeyboardButton(f"❤️ {R('donate')}", url=f"https://t.me/{OWNER_USERNAME}")
                ],[
                    InlineKeyboardButton(f"👥 {R('support_group')}", url=f"https://t.me/{GROUP_SUPPORT}"),
                    InlineKeyboardButton(f"📣 {R('support_channel')}", url=f"https://t.me/{UPDATES_CHANNEL}")
                ],[
                    InlineKeyboardButton(f"🌐 {R('source_code')}", url="https://github.com/levina-lab/video-stream")
                ],
            ]
        ),
        disable_web_page_preview=True,
    )


@Client.on_callback_query(filters.regex("quick_use"))
@check_blacklist()
async def quick_set(_, query: CallbackQuery):
    await query.answer(R("quick_use_notice"))
    await query.edit_message_text(
        R("quick_use").format(GROUP_SUPPORT),
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton(f"🔙 {R('go_back')}", callback_data="user_guide")]]
        ),
        disable_web_page_preview=True,
    )


@Client.on_callback_query(filters.regex("user_guide"))
@check_blacklist()
async def guide_set(_, query: CallbackQuery):
    await query.answer(R("user guide"))
    await query.edit_message_text(
        R("user_guide").format(me_user.username,
                               GROUP_SUPPORT),
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(f"» {R('user_guide_button')} «", callback_data="quick_use")
                ],[
                    InlineKeyboardButton(f"🔙 {R('go_back')}", callback_data="home_start")
                ],
            ]
        ),
    )


@Client.on_callback_query(filters.regex("command_list"))
@check_blacklist()
async def commands_set(_, query: CallbackQuery):
    user_id = query.from_user.id
    await query.answer(R("commands_menu_notice"))
    await query.edit_message_text(
        R("commands_menu").format(query.message.chat.first_name,
                     query.message.chat.id),
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(f"👮🏻‍♀️ {R('admins_commands')}", callback_data="admin_command"),
                ],[
                    InlineKeyboardButton(f"👩🏻‍💼 {R('users_commands')}", callback_data="user_command"),
                ],[
                    InlineKeyboardButton(R("sudoers_commands"), callback_data="sudo_command"),
                    InlineKeyboardButton(R("owners_commands"), callback_data="owner_command"),
                ],[
                    InlineKeyboardButton(f"🔙 {R('go_back')}", callback_data="home_start")
                ],
            ]
        ),
    )


@Client.on_callback_query(filters.regex("user_command"))
@check_blacklist()
async def user_set(_, query: CallbackQuery):
    await query.answer(R("basic_commands_notice"))
    await query.edit_message_text(
        R("basic_commands"),
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton(f"🔙 {R('go_back')}", callback_data="command_list")]]
        ),
    )


@Client.on_callback_query(filters.regex("admin_command"))
@check_blacklist()
async def admin_set(_, query: CallbackQuery):
    await query.answer(R("admin_commands_notice"))
    await query.edit_message_text(
        R("admin_commands"),
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton(f"🔙 {R('go_back')}", callback_data="command_list")]]
        ),
    )


@Client.on_callback_query(filters.regex("sudo_command"))
@check_blacklist()
async def sudo_set(_, query: CallbackQuery):
    user_id = query.from_user.id
    if user_id not in SUDO_USERS:
        await query.answer(f"⚠️ {R('sudo_no_permission')}", show_alert=True)
        return
    await query.answer(R("sudo_commands_notice"))
    await query.edit_message_text(
        R("sudo_commands"),
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton(f"🔙 {R('go_back')}", callback_data="command_list")]]
        ),
    )


@Client.on_callback_query(filters.regex("owner_command"))
@check_blacklist()
async def owner_set(_, query: CallbackQuery):
    user_id = query.from_user.id
    if user_id not in OWNER_ID:
        await query.answer(f"⚠️ {R('owner_no_permission')}", show_alert=True)
        return
    await query.answer(R("owner_commands_notice"))
    await query.edit_message_text(
        R("owner_commands"),
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton(f"🔙 {R('go_back')}", callback_data="command_list")]]
        ),
    )


@Client.on_callback_query(filters.regex("stream_menu_panel"))
@check_blacklist()
@require_admin(permissions=["can_manage_voice_chats"])
async def at_set_markup_menu(_, query: CallbackQuery):
    chat_id = query.message.chat.id
    user_id = query.message.from_user.id
    buttons = menu_markup(user_id)
    if chat_id in QUEUE:
        await query.answer(R("control_panel_opened"))
        await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(buttons))
    else:
        await query.answer(f"❌ {R('play_nothing')}", show_alert=True)


@Client.on_callback_query(filters.regex("stream_home_panel"))
@check_blacklist()
@require_admin(permissions=["can_manage_voice_chats"])
async def is_set_home_menu(_, query: CallbackQuery):
    user_id = query.message.from_user.id
    buttons = stream_markup(user_id)
    await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(buttons))


@Client.on_callback_query(filters.regex("set_close"))
@check_blacklist()
@require_admin(permissions=["can_manage_voice_chats"])
async def on_close_menu(_, query: CallbackQuery):
    await query.message.delete()


@Client.on_callback_query(filters.regex("close_panel"))
@check_blacklist()
async def in_close_panel(_, query: CallbackQuery):
    await query.message.delete()
