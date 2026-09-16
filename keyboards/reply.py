from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from config import WEBAPP_URL

def main_menu_keyboard(is_admin: bool = False) -> ReplyKeyboardMarkup:
    keyboard = [
        [
            KeyboardButton(text="🛍️ Open Store (Mini App)", web_app=WebAppInfo(url=WEBAPP_URL)),
            KeyboardButton(text="📋 Services List")
        ],
        [
            KeyboardButton(text="📦 My Orders"),
            KeyboardButton(text="ℹ️ About & FAQ")
        ],
        [
            KeyboardButton(text="💬 Contact Support")
        ]
    ]
    if is_admin:
        keyboard.append([KeyboardButton(text="⚡ Admin Dashboard")])

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        is_persistent=True
    )
