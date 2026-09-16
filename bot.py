import asyncio
import logging
import os
import sys
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from config import BOT_TOKEN, ADMIN_IDS
from database import init_db
from handlers import main_router

# Setup structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

async def health_check(request):
    """Health check endpoint for Render.com / Cloud Web Services"""
    return web.Response(text="✅ Telegram Service Bot is running 24/7!", content_type="text/plain")

async def start_web_server():
    """Starts a lightweight web server on the PORT assigned by Render"""
    port = int(os.getenv("PORT", 8080))
    app = web.Application()
    app.router.add_get("/", health_check)
    app.router.add_get("/health", health_check)
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logger.info(f"🌐 Health server running on port {port}")

async def main():
    if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        logger.error("❌ BOT_TOKEN is not set! Please provide your Telegram Bot Token in .env or Render Environment Variables.")
        print("\n" + "="*70)
        print("⚠️  SETUP REQUIRED: Please open .env and set your BOT_TOKEN from @BotFather.")
        print("="*70 + "\n")
        return

    logger.info("Initializing SQLite database...")
    await init_db()
    logger.info("Database initialized successfully.")

    # Start health check server for Render.com
    try:
        await start_web_server()
    except Exception as e:
        logger.warning(f"Could not start health web server (OK for local dev): {e}")

    # Initialize Bot & Dispatcher
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # Register all handlers
    dp.include_router(main_router)

    # Start Polling
    logger.info("🚀 Starting Telegram Bot polling...")
    try:
        # Delete webhook if previously set to enable polling
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped by user.")
