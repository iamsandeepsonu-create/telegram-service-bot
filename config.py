import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()

# Parse admin IDs list
admin_ids_raw = os.getenv("ADMIN_IDS", "")
ADMIN_IDS = [int(x.strip()) for x in admin_ids_raw.split(",") if x.strip().isdigit()]

DB_PATH = os.getenv("DB_PATH", "bot_database.db")

# Currency Conversion (1 USD to INR rate)
USD_TO_INR_RATE = float(os.getenv("USD_TO_INR_RATE", "85.0"))

# Ensure DB path is absolute if relative
if not os.path.isabs(DB_PATH):
    DB_PATH = str(BASE_DIR / DB_PATH)
