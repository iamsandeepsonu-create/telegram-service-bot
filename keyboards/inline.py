from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def services_menu_keyboard(services: list[dict]) -> InlineKeyboardMarkup:
    buttons = []
    for s in services:
        buttons.append([
            InlineKeyboardButton(
                text=f"{s['name']} — ${s['price']:.2f}",
                callback_data=f"service_{s['id']}"
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
                    text="🔙 Back to Catalog",
                    callback_data="back_to_services"
                )
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
                text=f"{status_emoji} {s['name']} (Click to Delete)",
                callback_data=f"admin_del_service_{s['id']}"
            )
        ])
    buttons.append([InlineKeyboardButton(text="🔙 Back to Admin Menu", callback_data="admin_back_to_menu")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)
