""" inline section button """

from pyrogram import (
  CallbackQuery,
  InlineKeyboardButton,
  InlineKeyboardMarkup,
  Message,
)


def stream_markup(user_id):
  buttons = [
    [
      InlineKeyboardButton(text="• Mᴇɴᴜ", callback_data="cbmenu"),
      InlineKeyboardButton(text="• Cʟᴏsᴇ", callback_data="cls"),
    ],
  ]
  return buttons


def menu_markup(user_id):
  buttons = [
    [
      InlineKeyboardButton(text="⏹", callback_data="cbstop"),
      InlineKeyboardButton(text="⏸", callback_data="cbresume"),
      InlineKeyboardButton(text="▶️", callback_data="cbresume"),
    ],
    [
      InlineKeyboardButton(text="🔇", callback_data="cbmute"),
      InlineKeyboardButton(text="🔊", callback_data="cbunmute"),
    ],
    [
      InlineKeyboardButton(text="🗑 Close", callback_data="cls"),
    ]
  ]
  return buttons


close_mark = InlineKeyboardMarkup(
  [
    [
      InlineKeyboardButton(
        "🗑 Close", callback_data="cls"
      )
    ]
  ]
)


back_mark = InlineKeyboardMarkup(
  [
    [
      InlineKeyboardButton(
        "🔙 Go Back", callback_data="cbmenu"
      )
    ]
  ]
)
