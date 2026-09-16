import asyncio
import logging
import os
import sys
from pathlib import Path
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from config import BOT_TOKEN, ADMIN_IDS, USD_TO_INR_RATE, WEBAPP_URL, BASE_DIR
from database import init_db, db
from database.db import format_price
from keyboards import admin_order_actions_keyboard
from handlers import main_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

bot_instance: Bot | None = None

# --- Web Server Endpoints for Render 24/7 & Telegram WebApp UI ---
async def health_check(request):
    return web.Response(text="✅ Telegram Service Bot & Store UI are running 24/7!", content_type="text/plain")

async def webapp_index(request):
    html_file = BASE_DIR / "webapp" / "index.html"
    if html_file.exists():
        return web.FileResponse(html_file)
    return web.Response(text="WebApp index.html not found", status=404)

async def api_get_services(request):
    services = await db.get_active_services()
    return web.json_response({"services": services, "count": len(services)})

async def api_create_order(request):
    global bot_instance
    try:
        data = await request.json()
        user_id = int(data.get("user_id", 0))
        username = data.get("username")
        full_name = data.get("full_name", "Telegram User")
        service_id = int(data.get("service_id"))
        requirements = data.get("requirements", "").strip()
        currency = data.get("currency", "INR")

        if not service_id or len(requirements) < 3:
            return web.json_response({"success": False, "error": "Invalid service or requirements"}, status=400)

        service = await db.get_service_by_id(service_id)
        if not service:
            return web.json_response({"success": False, "error": "Service not found"}, status=404)

        if user_id > 0:
            await db.add_or_update_user(user_id, username, full_name, detected_currency=currency)

        order_id = await db.create_order(
            user_id=user_id,
            service_id=service_id,
            requirements=requirements
        )

        price_inr = service["price"]
        price_usd = price_inr / USD_TO_INR_RATE
        price_display = format_price(price_inr, currency)

        if bot_instance and user_id > 0:
            try:
                client_msg = (
                    f"🎉 **Order Placed Successfully! (Order #{order_id})**\n\n"
                    f"🏷️ **Service:** {service['name']}\n"
                    f"💵 **Price:** `{price_display}`\n"
                    f"⏱️ **Duration:** `{service['duration']}`\n\n"
                    f"📋 **Requirements:**\n_{requirements}_\n\n"
                    "Our team has received your order and will start immediately!"
                )
                await bot_instance.send_message(chat_id=user_id, text=client_msg, parse_mode="Markdown")
            except Exception as e:
                logger.warning(f"Could not send confirmation to user {user_id}: {e}")

        if bot_instance:
            admin_alert_text = (
                f"🚨 **NEW SERVICE ORDER! (Order #{order_id})**\n\n"
                f"👤 **Customer:** {full_name} (@{username or 'NoUsername'})\n"
                f"🆔 **User ID:** `{user_id}`\n"
                f"🌐 **Currency:** `{currency}`\n"
                f"🏷️ **Service:** {service['name']}\n"
                f"💰 **Amount:** `₹{price_inr:,.0f}` (or `${price_usd:.2f} USD`)\n"
                f"⏱️ **Duration:** `{service['duration']}`\n\n"
                f"📝 **Requirements:**\n{requirements}"
            )
            for admin_id in ADMIN_IDS:
                try:
                    await bot_instance.send_message(
                        chat_id=admin_id,
                        text=admin_alert_text,
                        reply_markup=admin_order_actions_keyboard(order_id),
                        parse_mode="Markdown"
                    )
                except Exception as e:
                    logger.warning(f"Failed to alert admin {admin_id}: {e}")

        return web.json_response({"success": True, "order_id": order_id})
    except Exception as err:
        logger.error(f"Error in api_create_order: {err}")
        return web.json_response({"success": False, "error": str(err)}, status=500)

async def start_web_server():
    port = int(os.getenv("PORT", 8080))
    app = web.Application()
    
    app.router.add_get("/", health_check)
    app.router.add_get("/health", health_check)
    app.router.add_get("/webapp", webapp_index)
    app.router.add_get("/api/services", api_get_services)
    app.router.add_post("/api/order", api_create_order)

    webapp_dir = BASE_DIR / "webapp"
    if webapp_dir.exists():
        app.router.add_static("/webapp/", path=str(webapp_dir), name="webapp")

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logger.info(f"🌐 Server & WebApp UI running on port {port}")

async def main():
    global bot_instance

    if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        logger.error("❌ BOT_TOKEN is not set! Please set BOT_TOKEN in .env or Render Environment Variables.")
        return

    logger.info("Initializing SQLite database...")
    await init_db()
    logger.info("Database initialized successfully.")

    try:
        await start_web_server()
    except Exception as e:
        logger.warning(f"Could not start web server: {e}")

    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    bot_instance = bot
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # Register all handlers
    dp.include_router(main_router)

    logger.info("🚀 Starting Telegram Bot polling...")
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped by user.")
