from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def main_menu_keyboard(is_admin: bool = False) -> ReplyKeyboardMarkup:
    keyboard = [
        [
            KeyboardButton(text="🛍️ Services Catalog"),
            KeyboardButton(text="📦 My Orders")
        ],
        [
            KeyboardButton(text="ℹ️ About & FAQ"),
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
