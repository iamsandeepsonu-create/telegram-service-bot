from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from config import ADMIN_IDS
from database import db
from states.order_states import AdminAddService, AdminBroadcast
from keyboards import (
    admin_panel_keyboard,
    admin_manage_services_keyboard,
)

admin_router = Router()

def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS

@admin_router.message(F.text == "⚡ Admin Dashboard")
@admin_router.message(Command("admin"))
async def show_admin_dashboard(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer("⛔ Access denied. This menu is for administrators only.")
        return

    text = (
        "⚡ **Admin Management Console**\n\n"
        "Select an action from the control panel below:"
    )
    await message.answer(text, reply_markup=admin_panel_keyboard(), parse_mode="Markdown")

@admin_router.callback_query(F.data == "admin_back_to_menu")
async def cb_admin_back_to_menu(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Access denied.")
        return

    text = (
        "⚡ **Admin Management Console**\n\n"
        "Select an action from the control panel below:"
    )
    await callback.message.edit_text(text, reply_markup=admin_panel_keyboard(), parse_mode="Markdown")
    await callback.answer()

@admin_router.callback_query(F.data == "admin_stats")
async def cb_admin_stats(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Access denied.")
        return

    stats = await db.get_stats()
    text = (
        "📊 **Bot Business Analytics**\n\n"
        f"👥 **Total Registered Users:** `{stats['total_users']}`\n"
        f"📦 **Total Orders Placed:** `{stats['total_orders']}`\n"
        f"✅ **Completed Orders:** `{stats['completed_orders']}`\n"
        f"💰 **Total Completed Revenue:** `${stats['total_revenue']:.2f}`\n"
    )
    await callback.message.edit_text(text, reply_markup=admin_panel_keyboard(), parse_mode="Markdown")
    await callback.answer()

@admin_router.callback_query(F.data == "admin_orders")
async def cb_admin_recent_orders(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Access denied.")
        return

    orders = await db.get_recent_orders(limit=10)
    if not orders:
        await callback.message.edit_text("📋 No orders found yet.", reply_markup=admin_panel_keyboard())
        await callback.answer()
        return

    lines = ["📋 **Latest 10 Orders:**\n"]
    for o in orders:
        lines.append(
            f"• **#{o['id']}** | {o['service_name']} (${o['price']:.2f})\n"
            f"  Client: {o['full_name']} (@{o['username'] or 'NoUser'})\n"
            f"  Status: `{o['status']}` | Date: `{o['created_at'][:10]}`"
        )

    await callback.message.edit_text("\n\n".join(lines), reply_markup=admin_panel_keyboard(), parse_mode="Markdown")
    await callback.answer()

# --- Add Service FSM ---
@admin_router.callback_query(F.data == "admin_add_service")
async def cb_start_add_service(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("Access denied.")
        return

    await state.set_state(AdminAddService.waiting_for_name)
    await callback.message.edit_text(
        "➕ **Adding New Service**\n\n"
        "Please enter the **Title / Name** of the new service:\n"
        "*(Example: 📱 Mobile App UI Design)*",
        parse_mode="Markdown"
    )
    await callback.answer()

@admin_router.message(AdminAddService.waiting_for_name, F.text)
async def process_service_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text.strip())
    await state.set_state(AdminAddService.waiting_for_description)
    await message.answer("📝 Now enter a detailed **Description** for this service:")

@admin_router.message(AdminAddService.waiting_for_description, F.text)
async def process_service_desc(message: Message, state: FSMContext):
    await state.update_data(description=message.text.strip())
    await state.set_state(AdminAddService.waiting_for_price)
    await message.answer("💵 Enter the **Price in USD** (number only, e.g. 49.99):")

@admin_router.message(AdminAddService.waiting_for_price, F.text)
async def process_service_price(message: Message, state: FSMContext):
    try:
        price = float(message.text.strip().replace("$", ""))
    except ValueError:
        await message.answer("⚠️ Invalid price. Please enter a valid number (e.g. 29.99):")
        return

    await state.update_data(price=price)
    await state.set_state(AdminAddService.waiting_for_duration)
    await message.answer("⏱️ Enter estimated **Turnaround / Delivery Time** (e.g. `2-3 Days` or `24 Hours`):")

@admin_router.message(AdminAddService.waiting_for_duration, F.text)
async def process_service_duration(message: Message, state: FSMContext):
    duration = message.text.strip()
    data = await state.get_data()
    await state.clear()

    service_id = await db.add_service(
        name=data['name'],
        description=data['description'],
        price=data['price'],
        duration=duration
    )

    success_msg = (
        f"✅ **Service Added Successfully! (ID: {service_id})**\n\n"
        f"🏷️ **Name:** {data['name']}\n"
        f"💵 **Price:** `${data['price']:.2f}`\n"
        f"⏱️ **Delivery:** `{duration}`\n\n"
        "It is now live in the customer catalog!"
    )
    await message.answer(success_msg, reply_markup=admin_panel_keyboard(), parse_mode="Markdown")

# --- Manage / Delete Services ---
@admin_router.callback_query(F.data == "admin_manage_services")
async def cb_manage_services(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Access denied.")
        return

    services = await db.get_active_services()
    if not services:
        await callback.message.edit_text("No active services to manage.", reply_markup=admin_panel_keyboard())
        await callback.answer()
        return

    await callback.message.edit_text(
        "🗑️ **Manage Services**\n\nTap any service below to delete/deactivate it from catalog:",
        reply_markup=admin_manage_services_keyboard(services),
        parse_mode="Markdown"
    )
    await callback.answer()

@admin_router.callback_query(F.data.startswith("admin_del_service_"))
async def cb_delete_service(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Access denied.")
        return

    service_id = int(callback.data.split("_")[3])
    await db.delete_service(service_id)
    await callback.answer("Service deleted!", show_alert=True)

    services = await db.get_active_services()
    if not services:
        await callback.message.edit_text("All services deleted.", reply_markup=admin_panel_keyboard())
    else:
        await callback.message.edit_reply_markup(reply_markup=admin_manage_services_keyboard(services))

# --- Broadcast Message to All Users ---
@admin_router.callback_query(F.data == "admin_broadcast")
async def cb_start_broadcast(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("Access denied.")
        return

    await state.set_state(AdminBroadcast.waiting_for_message)
    await callback.message.edit_text(
        "📢 **Broadcast Announcement**\n\n"
        "Send the text message you want to broadcast to **all registered users**:\n"
        "*(Type /cancel to abort)*",
        parse_mode="Markdown"
    )
    await callback.answer()

@admin_router.message(AdminBroadcast.waiting_for_message, F.text)
async def process_broadcast_message(message: Message, state: FSMContext, bot: Bot):
    if message.text.strip() == "/cancel":
        await state.clear()
        await message.answer("❌ Broadcast aborted.", reply_markup=admin_panel_keyboard())
        return

    broadcast_text = message.text
    await state.clear()

    user_ids = await db.get_all_user_ids()
    sent_count = 0
    failed_count = 0

    status_msg = await message.answer(f"⏳ Broadcasting to {len(user_ids)} users...")

    for uid in user_ids:
        try:
            await bot.send_message(
                chat_id=uid,
                text=f"📢 **Announcement:**\n\n{broadcast_text}",
                parse_mode="Markdown"
            )
            sent_count += 1
        except Exception:
            failed_count += 1

    await status_msg.edit_text(
        f"✅ **Broadcast Completed!**\n\n"
        f"• Successfully sent: `{sent_count}`\n"
        f"• Failed/Blocked: `{failed_count}`",
        reply_markup=admin_panel_keyboard(),
        parse_mode="Markdown"
    )

# --- Status Update Action Callbacks ---
@admin_router.callback_query(F.data.startswith("status_"))
async def cb_update_order_status(callback: CallbackQuery, bot: Bot):
    if not is_admin(callback.from_user.id):
        await callback.answer("Access denied.")
        return

    parts = callback.data.split("_")
    status_type = parts[1] # inprogress, completed, cancelled
    order_id = int(parts[2])

    status_map = {
        "inprogress": "In Progress",
        "completed": "Completed",
        "cancelled": "Cancelled"
    }
    new_status = status_map.get(status_type, "Pending")
    await db.update_order_status(order_id, new_status)

    order = await db.get_order_by_id(order_id)
    await callback.answer(f"Order #{order_id} marked as {new_status}!", show_alert=True)
    await callback.message.edit_text(
        f"{callback.message.text}\n\n📌 **Status Updated to:** `{new_status}` by Admin."
    )

    # Notify client directly
    if order:
        client_id = order['user_id']
        client_notice = {
            "In Progress": f"⚙️ **Good news!** Your order **#{order_id} ({order['service_name']})** is now **In Progress**.",
            "Completed": f"🎉 **Order Completed!** Your order **#{order_id} ({order['service_name']})** has been fulfilled. Thank you!",
            "Cancelled": f"❌ Your order **#{order_id} ({order['service_name']})** has been cancelled. Please contact support for details."
        }.get(new_status)

        if client_notice:
            try:
                await bot.send_message(chat_id=client_id, text=client_notice, parse_mode="Markdown")
            except Exception:
                pass
