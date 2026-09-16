from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from config import ADMIN_IDS
from database import db
from database.db import format_price, get_price_display
from keyboards import (
    main_menu_keyboard,
    services_menu_keyboard,
    service_detail_keyboard,
)
from keyboards.inline import currency_switch_keyboard

user_router = Router()

def detect_default_currency(language_code: str | None) -> str:
    """Auto-detect INR for Indian users and USD for foreign visitors."""
    if not language_code:
        return "INR"
    
    code = language_code.lower()
    
    # Non-Indian international language codes
    foreign_codes = ["ru", "es", "fr", "de", "ar", "ja", "zh", "pt", "it", "tr", "pl", "uk", "vi", "id", "ko"]
    if any(code.startswith(fc) for fc in foreign_codes):
        return "USD"
    
    # Default to INR
    return "INR"

@user_router.message(CommandStart())
async def cmd_start(message: Message):
    user = message.from_user
    if not user:
        return

    detected_currency = detect_default_currency(user.language_code)

    # Record user in database with auto-detected currency
    await db.add_or_update_user(
        user_id=user.id,
        username=user.username,
        full_name=user.full_name,
        detected_currency=detected_currency
    )

    is_admin = user.id in ADMIN_IDS

    currency_note = "🇮🇳 Pricing set to **INR (₹)**" if detected_currency == "INR" else "🌍 Pricing set to **USD ($)**"

    welcome_text = (
        f"👋 **Hello {user.first_name}!**\n\n"
        "Welcome to our **Professional Services Bot**.\n"
        "Here you can explore our premium services, place instant orders, "
        "and track your project delivery in real time.\n\n"
        f"💱 _{currency_note} (You can switch anytime in catalog)_\n\n"
        "👇 *Use the menu below to get started:*"
    )

    await message.answer(
        welcome_text,
        reply_markup=main_menu_keyboard(is_admin=is_admin),
        parse_mode="Markdown"
    )

@user_router.message(F.text == "🛍️ Services Catalog")
@user_router.message(Command("services"))
async def show_services(message: Message):
    user_id = message.from_user.id
    currency = await db.get_user_currency(user_id)
    services = await db.get_active_services()

    if not services:
        await message.answer("⚠️ No services are currently available. Please check back soon!")
        return

    currency_flag = "🇮🇳 INR (₹)" if currency == "INR" else "🌍 USD ($)"
    text = (
        f"💼 **Our Available Services & Packages:**\n"
        f"Currency: `{currency_flag}`\n\n"
        "_Select a service below for details & ordering:_"
    )
    await message.answer(
        text,
        reply_markup=services_menu_keyboard(services, currency=currency),
        parse_mode="Markdown"
    )

@user_router.callback_query(F.data == "open_currency_menu")
async def cb_open_currency_menu(callback: CallbackQuery):
    user_id = callback.from_user.id
    current_currency = await db.get_user_currency(user_id)
    text = (
        "💱 **Choose Your Preferred Currency:**\n\n"
        "• **🇮🇳 INR (₹)** — Indian Rupee\n"
        "• **🌍 USD ($)** — US Dollar (International)\n\n"
        "Select an option below to update all catalog prices:"
    )
    await callback.message.edit_text(
        text,
        reply_markup=currency_switch_keyboard(current_currency),
        parse_mode="Markdown"
    )
    await callback.answer()

@user_router.callback_query(F.data.startswith("set_currency_"))
async def cb_set_currency(callback: CallbackQuery):
    new_currency = callback.data.split("_")[2] # INR or USD
    user_id = callback.from_user.id
    await db.set_user_currency(user_id, new_currency)

    services = await db.get_active_services()
    currency_flag = "🇮🇳 INR (₹)" if new_currency == "INR" else "🌍 USD ($)"
    
    await callback.answer(f"Currency changed to {currency_flag}!", show_alert=True)
    
    text = (
        f"💼 **Our Available Services & Packages:**\n"
        f"Currency: `{currency_flag}`\n\n"
        "_Select a service below for details & ordering:_"
    )
    await callback.message.edit_text(
        text,
        reply_markup=services_menu_keyboard(services, currency=new_currency),
        parse_mode="Markdown"
    )

@user_router.callback_query(F.data == "back_to_services")
async def cb_back_to_services(callback: CallbackQuery):
    user_id = callback.from_user.id
    currency = await db.get_user_currency(user_id)
    services = await db.get_active_services()

    if not services:
        await callback.message.edit_text("⚠️ No services currently available.")
        await callback.answer()
        return

    currency_flag = "🇮🇳 INR (₹)" if currency == "INR" else "🌍 USD ($)"
    text = (
        f"💼 **Our Available Services & Packages:**\n"
        f"Currency: `{currency_flag}`\n\n"
        "_Select a service below for details & ordering:_"
    )
    await callback.message.edit_text(
        text,
        reply_markup=services_menu_keyboard(services, currency=currency),
        parse_mode="Markdown"
    )
    await callback.answer()

@user_router.callback_query(F.data.startswith("service_"))
async def cb_service_detail(callback: CallbackQuery):
    try:
        service_id = int(callback.data.split("_")[1])
    except (ValueError, IndexError):
        await callback.answer("Invalid service.")
        return

    service = await db.get_service_by_id(service_id)
    if not service:
        await callback.answer("Service not found.", show_alert=True)
        return

    user_id = callback.from_user.id
    currency = await db.get_user_currency(user_id)
    formatted_price = format_price(service['price'], currency)

    detail_text = (
        f"✨ **{service['name']}**\n\n"
        f"📝 **Description:**\n{service['description']}\n\n"
        f"💵 **Price:** `{formatted_price}`\n"
        f"⏱️ **Delivery Time:** `{service['duration']}`\n\n"
        "Ready to start? Click **Order This Service** below!"
    )

    await callback.message.edit_text(
        detail_text,
        reply_markup=service_detail_keyboard(service_id),
        parse_mode="Markdown"
    )
    await callback.answer()

@user_router.message(F.text == "📦 My Orders")
@user_router.message(Command("myorders"))
async def show_user_orders(message: Message):
    user_id = message.from_user.id
    currency = await db.get_user_currency(user_id)
    orders = await db.get_user_orders(user_id)

    if not orders:
        await message.answer(
            "📦 **You don't have any orders yet.**\n"
            "Browse our catalog using **🛍️ Services Catalog** to place your first order!",
            parse_mode="Markdown"
        )
        return

    status_emojis = {
        "Pending": "⏳ Pending Review",
        "In Progress": "⚙️ In Progress",
        "Completed": "✅ Completed",
        "Cancelled": "❌ Cancelled"
    }

    lines = ["📋 **Your Order History:**\n"]
    for o in orders:
        status_label = status_emojis.get(o['status'], o['status'])
        price_str = get_price_display(o['price'], currency)
        lines.append(
            f"• **Order #{o['id']}**: {o['service_name']} ({price_str})\n"
            f"  Status: `{status_label}` | Date: `{o['created_at'][:10]}`"
        )

    await message.answer("\n\n".join(lines), parse_mode="Markdown")

@user_router.message(F.text == "ℹ️ About & FAQ")
@user_router.message(Command("about"))
async def show_about_faq(message: Message):
    faq_text = (
        "ℹ️ **Frequently Asked Questions (FAQ)**\n\n"
        "**Q: What currencies do you accept?**\n"
        "A: We support **Indian Rupee (INR ₹)** for clients in India (UPI, GPay, Bank) and **US Dollar (USD $)** for international clients (Cards, Crypto, PayPal).\n\n"
        "**Q: How does the ordering process work?**\n"
        "A: Select a service, provide your project requirements & reference files, and confirm. Our team will start immediately.\n\n"
        "**Q: How do I receive my completed work?**\n"
        "A: Once finished, the deliverables will be sent directly through this Telegram bot!\n\n"
        "💡 *Need custom work? Contact our support team!*"
    )
    await message.answer(faq_text, parse_mode="Markdown")

@user_router.message(F.text == "💬 Contact Support")
@user_router.message(Command("support"))
async def contact_support(message: Message):
    support_text = (
        "💬 **Customer Support & Inquiries**\n\n"
        "Have questions, custom inquiries, or need assistance?\n"
        "Reach out directly to our admin team:\n\n"
        "👉 **Admin Contact:** @YourSupportUsername\n"
        "📧 **Email:** support@example.com\n\n"
        "We typically respond within 1–2 hours!"
    )
    await message.answer(support_text, parse_mode="Markdown")
