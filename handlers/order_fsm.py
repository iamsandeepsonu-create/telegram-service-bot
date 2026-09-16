from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from config import ADMIN_IDS
from database import db
from states.order_states import OrderPlacement
from keyboards import (
    attachment_skip_keyboard,
    order_confirm_keyboard,
    admin_order_actions_keyboard,
)

order_router = Router()

@order_router.callback_query(F.data.startswith("order_service_"))
async def start_order_process(callback: CallbackQuery, state: FSMContext):
    try:
        service_id = int(callback.data.split("_")[2])
    except (ValueError, IndexError):
        await callback.answer("Invalid service.")
        return

    service = await db.get_service_by_id(service_id)
    if not service:
        await callback.answer("Service not found.", show_alert=True)
        return

    await state.update_data(
        service_id=service_id,
        service_name=service['name'],
        price=service['price'],
        duration=service['duration']
    )

    await state.set_state(OrderPlacement.waiting_for_requirements)

    text = (
        f"📝 **Placing Order for:** `{service['name']}`\n\n"
        "Please type your **project requirements or instructions** in detail.\n"
        "*(Example: Features needed, colors, deadline, specific instructions)*"
    )

    await callback.message.edit_text(text, parse_mode="Markdown")
    await callback.answer()

@order_router.message(OrderPlacement.waiting_for_requirements, F.text)
async def process_requirements(message: Message, state: FSMContext):
    requirements = message.text.strip()
    if len(requirements) < 5:
        await message.answer("⚠️ Please provide more detailed instructions (minimum 5 characters).")
        return

    await state.update_data(requirements=requirements)
    await state.set_state(OrderPlacement.waiting_for_attachment)

    text = (
        "📎 **Reference Files / Attachments (Optional)**\n\n"
        "You can now send a **Photo**, **Document/File**, or **Link** relevant to your order.\n\n"
        "If you don't have any files, simply tap **⏩ Skip Attachment** below:"
    )

    await message.answer(
        text,
        reply_markup=attachment_skip_keyboard(),
        parse_mode="Markdown"
    )

@order_router.callback_query(OrderPlacement.waiting_for_attachment, F.data == "skip_attachment")
async def skip_attachment(callback: CallbackQuery, state: FSMContext):
    await state.update_data(attachment_file_id=None)
    await show_order_summary(callback.message, state, is_edit=True)
    await callback.answer()

@order_router.message(OrderPlacement.waiting_for_attachment, F.photo | F.document)
async def process_attachment(message: Message, state: FSMContext):
    file_id = None
    if message.photo:
        file_id = message.photo[-1].file_id
    elif message.document:
        file_id = message.document.file_id

    await state.update_data(attachment_file_id=file_id)
    await show_order_summary(message, state, is_edit=False)

async def show_order_summary(message: Message, state: FSMContext, is_edit: bool = False):
    data = await state.get_data()
    await state.set_state(OrderPlacement.confirm_order)

    has_file = "Attached ✅" if data.get("attachment_file_id") else "None"

    summary_text = (
        "🔍 **Review Your Order Details:**\n\n"
        f"🏷️ **Service:** {data['service_name']}\n"
        f"💵 **Total Price:** `${data['price']:.2f}`\n"
        f"⏱️ **Estimated Delivery:** `{data['duration']}`\n"
        f"📎 **Attachments:** `{has_file}`\n\n"
        f"📋 **Requirements Brief:**\n_{data['requirements']}_\n\n"
        "Confirm your order by clicking the button below:"
    )

    if is_edit:
        await message.edit_text(
            summary_text,
            reply_markup=order_confirm_keyboard(),
            parse_mode="Markdown"
        )
    else:
        await message.answer(
            summary_text,
            reply_markup=order_confirm_keyboard(),
            parse_mode="Markdown"
        )

@order_router.callback_query(OrderPlacement.confirm_order, F.data == "confirm_order_submit")
async def confirm_order_submission(callback: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    user = callback.from_user

    # Create Order in DB
    order_id = await db.create_order(
        user_id=user.id,
        service_id=data['service_id'],
        requirements=data['requirements'],
        file_id=data.get('attachment_file_id')
    )

    await state.clear()

    # Success message for client
    success_text = (
        f"🎉 **Order Placed Successfully! (Order #{order_id})**\n\n"
        f"Thank you, {user.first_name}! Your request for **{data['service_name']}** has been submitted.\n\n"
        "📌 **What happens next?**\n"
        "Our team will review your order and start working on it right away. "
        "You will receive live status notifications here.\n\n"
        "Track anytime using the **📦 My Orders** menu."
    )

    await callback.message.edit_text(success_text, parse_mode="Markdown")
    await callback.answer()

    # Notify Admins
    admin_alert_text = (
        f"🚨 **NEW ORDER RECEIVED! (Order #{order_id})**\n\n"
        f"👤 **Customer:** {user.full_name} (@{user.username or 'NoUsername'})\n"
        f"🆔 **User ID:** `{user.id}`\n"
        f"🏷️ **Service:** {data['service_name']} (${data['price']:.2f})\n"
        f"⏱️ **Duration:** `{data['duration']}`\n\n"
        f"📝 **Client Requirements:**\n{data['requirements']}"
    )

    for admin_id in ADMIN_IDS:
        try:
            if data.get("attachment_file_id"):
                await bot.send_message(
                    chat_id=admin_id,
                    text=admin_alert_text,
                    reply_markup=admin_order_actions_keyboard(order_id),
                    parse_mode="Markdown"
                )
                # Forward or send file
                try:
                    await bot.send_document(
                        chat_id=admin_id,
                        document=data["attachment_file_id"],
                        caption=f"📎 Attachment for Order #{order_id}"
                    )
                except Exception:
                    pass
            else:
                await bot.send_message(
                    chat_id=admin_id,
                    text=admin_alert_text,
                    reply_markup=admin_order_actions_keyboard(order_id),
                    parse_mode="Markdown"
                )
        except Exception as e:
            print(f"Failed to alert admin {admin_id}: {e}")

@order_router.callback_query(F.data == "cancel_order")
async def cancel_order_flow(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("❌ Order cancelled. You can browse the catalog anytime.")
    await callback.answer()
