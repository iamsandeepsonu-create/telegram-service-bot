from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database.db import get_price_display, THEMES

def services_menu_keyboard(services: list[dict], currency: str = "INR", theme: dict | None = None) -> InlineKeyboardMarkup:
    """
    Creates full-width vertical stacked buttons matching the user's screenshot.
    """
    bullet = theme.get("icon", "🔵") if theme else "🔵"
    buttons = []

    for index, s in enumerate(services):
        # 1 service per row (full-width stacked button like in screenshot)
        service_name = s['name'].upper()
        # Highlight special item with green emoji if desired
        item_bullet = "🟢" if index == 4 else bullet
        
        button_text = f"{item_bullet} {service_name}"
        
        buttons.append([
            InlineKeyboardButton(
                text=button_text,
                callback_data=f"service_{s['id']}"
            )
        ])

    # Bottom helper row: Currency Switcher
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
                InlineKeyboardButton(text="🎨 Change Theme Color", callback_data="admin_theme_menu")
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
                text=f"{status_emoji} {s['name'].upper()} (₹{s['price']:,.0f})",
                callback_data=f"admin_del_service_{s['id']}"
            )
        ])
    buttons.append([InlineKeyboardButton(text="🔙 Back to Admin Menu", callback_data="admin_back_to_menu")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)
