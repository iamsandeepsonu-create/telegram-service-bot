from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from database.db import get_price_display, THEMES
from config import WEBAPP_URL

def services_menu_keyboard(services: list[dict], currency: str = "INR", theme: dict | None = None) -> InlineKeyboardMarkup:
    bullet = theme.get("bullet", "🔹") if theme else "🔹"
    buttons = []
    
    # Prominent Mini App button at the top
    buttons.append([
        InlineKeyboardButton(
            text="📱 Open Full-Screen Store (Mini App) 🚀",
            web_app=WebAppInfo(url=WEBAPP_URL)
        )
    ])

    for s in services:
        price_str = get_price_display(s['price'], currency)
        buttons.append([
            InlineKeyboardButton(
                text=f"{bullet} {s['name']} — {price_str}",
                callback_data=f"service_{s['id']}"
            )
        ])
    
    currency_label = "🇮🇳 Currency: INR (₹) - Tap to switch" if currency == "INR" else "🌍 Currency: USD ($) - Tap to switch"
    buttons.append([
        InlineKeyboardButton(
            text=f"💱 {currency_label}",
            callback_data="open_currency_menu"
        )
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def service_detail_keyboard(service_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🛒 Order This Service",
                    callback_data=f"order_service_{service_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📱 Open Mini App Store",
                    web_app=WebAppInfo(url=WEBAPP_URL)
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔙 Back to Catalog",
                    callback_data="back_to_services"
                )
            ]
        ]
    )

def currency_switch_keyboard(current_currency: str = "INR") -> InlineKeyboardMarkup:
    inr_prefix = "✅ " if current_currency == "INR" else ""
    usd_prefix = "✅ " if current_currency == "USD" else ""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=f"{inr_prefix}🇮🇳 Indian Rupee (INR ₹)", callback_data="set_currency_INR"),
                InlineKeyboardButton(text=f"{usd_prefix}🌍 US Dollar (USD $)", callback_data="set_currency_USD")
            ],
            [
                InlineKeyboardButton(text="🔙 Back to Services", callback_data="back_to_services")
            ]
        ]
    )

def attachment_skip_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⏩ Skip Attachment",
                    callback_data="skip_attachment"
                )
            ],
            [
                InlineKeyboardButton(
                    text="❌ Cancel Order",
                    callback_data="cancel_order"
                )
            ]
        ]
    )

def order_confirm_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Confirm & Submit Order",
                    callback_data="confirm_order_submit"
                )
            ],
            [
                InlineKeyboardButton(
                    text="❌ Cancel Order",
                    callback_data="cancel_order"
                )
            ]
        ]
    )

def admin_panel_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📊 Revenue & Stats", callback_data="admin_stats"),
                InlineKeyboardButton(text="📋 Recent Orders", callback_data="admin_orders")
            ],
            [
                InlineKeyboardButton(text="➕ Add New Service", callback_data="admin_add_service"),
                InlineKeyboardButton(text="🗑️ Manage / Delete Services", callback_data="admin_manage_services")
            ],
            [
                InlineKeyboardButton(text="🎨 Change Theme Color", callback_data="admin_theme_menu")
            ],
            [
                InlineKeyboardButton(text="📱 Preview Mini App", web_app=WebAppInfo(url=WEBAPP_URL))
            ],
            [
                InlineKeyboardButton(text="📢 Broadcast Announcement", callback_data="admin_broadcast")
            ]
        ]
    )

def admin_theme_selector_keyboard(current_theme_key: str = "BLUE") -> InlineKeyboardMarkup:
    buttons = []
    for key, val in THEMES.items():
        prefix = "✅ " if key == current_theme_key else ""
        buttons.append([
            InlineKeyboardButton(
                text=f"{prefix}{val['icon']} {val['name']}",
                callback_data=f"admin_set_theme_{key}"
            )
        ])
    buttons.append([InlineKeyboardButton(text="🔙 Back to Admin Menu", callback_data="admin_back_to_menu")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def admin_order_actions_keyboard(order_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="⏳ In Progress", callback_data=f"status_inprogress_{order_id}"),
                InlineKeyboardButton(text="✅ Complete", callback_data=f"status_completed_{order_id}")
            ],
            [
                InlineKeyboardButton(text="❌ Cancel Order", callback_data=f"status_cancelled_{order_id}")
            ]
        ]
    )

def admin_manage_services_keyboard(services: list[dict]) -> InlineKeyboardMarkup:
    buttons = []
    for s in services:
        status_emoji = "🟢" if s.get("is_active", 1) else "🔴"
        buttons.append([
            InlineKeyboardButton(
                text=f"{status_emoji} {s['name']} (₹{s['price']:,.0f})",
                callback_data=f"admin_del_service_{s['id']}"
            )
        ])
    buttons.append([InlineKeyboardButton(text="🔙 Back to Admin Menu", callback_data="admin_back_to_menu")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)
