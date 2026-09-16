from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from database.db import get_price_display, THEMES
from config import WEBAPP_URL

def services_menu_keyboard(services: list[dict], currency: str = "INR", theme: dict | None = None) -> InlineKeyboardMarkup:
    buttons = []
    
    # Open full UI Store
    buttons.append([
        InlineKeyboardButton(
            text="🛍️ OPEN SERVICES MENU 🚀",
            web_app=WebAppInfo(url=WEBAPP_URL)
        )
    ])

    for s in services:
        service_name = s['name'].upper()
        buttons.append([
            InlineKeyboardButton(
                text=f"🔵 {service_name}",
                callback_data=f"service_{s['id']}"
            )
        ])

    currency_label = "🇮🇳 INR (₹)" if currency == "INR" else "🌍 USD ($)"
    buttons.append([
        InlineKeyboardButton(
            text=f"💱 Currency: {currency_label} (Tap to Switch)",
            callback_data="open_currency_menu"
        )
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)

def service_detail_keyboard(service_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🛒 ORDER THIS SERVICE",
                    callback_data=f"order_service_{service_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📱 OPEN IN MENU UI",
                    web_app=WebAppInfo(url=WEBAPP_URL)
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔙 BACK TO CATALOG",
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
                InlineKeyboardButton(text="📱 Preview Services Menu", web_app=WebAppInfo(url=WEBAPP_URL))
            ],
            [
                InlineKeyboardButton(text="📢 Broadcast Announcement", callback_data="admin_broadcast")
            ]
        ]
    )

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
                text=f"{status_emoji} {s['name'].upper()} (₹{s['price']:,.0f})",
                callback_data=f"admin_del_service_{s['id']}"
            )
        ])
    buttons.append([InlineKeyboardButton(text="🔙 Back to Admin Menu", callback_data="admin_back_to_menu")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)
