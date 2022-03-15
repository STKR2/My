""" inline section button """

from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from driver.utils import R


def stream_markup(user_id):
    buttons = [
        [
            InlineKeyboardButton(text=f"• {R('inline_menu')}", callback_data=f'stream_menu_panel | {user_id}'),
            InlineKeyboardButton(text=f"• {R('inline_close')}", callback_data=f'set_close'),
        ],
    ]
    return buttons


def menu_markup(user_id):
    buttons = [
        [
            InlineKeyboardButton(text="⏹", callback_data=f'set_stop | {user_id}'),
            InlineKeyboardButton(text="⏸", callback_data=f'set_pause | {user_id}'),
            InlineKeyboardButton(text="▶️", callback_data=f'set_resume | {user_id}'),
            InlineKeyboardButton(text="⏭", callback_data=f'set_skip | {user_id}'),
        ],
        [
            InlineKeyboardButton(text="🔇", callback_data=f'set_mute | {user_id}'),
            InlineKeyboardButton(text="🔊", callback_data=f'set_unmute | {user_id}'),
        ],
        [
            InlineKeyboardButton(text=f"🔙 {R('go_back')}", callback_data='stream_home_panel'),
        ]
    ]
    return buttons


close_mark = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton(
                f"🗑 {R('close')}", callback_data="set_close"
            )
        ]
    ]
)

back_mark = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton(
                f"🔙 {R('go_back')}", callback_data="stream_menu_panel"
            )
        ]
    ]
)
