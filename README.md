# 🚀 Professional Telegram Service Selling Bot

A complete, production-ready Telegram Bot built with **Python 3**, **`aiogram 3.x`**, and **SQLite (Async)** for selling services, managing orders, and communicating with clients.

---

## ✨ Features

- 🛍️ **Interactive Service Catalog**: Beautiful inline buttons showcasing packages, turnaround times, and pricing.
- 📝 **Intake Form Flow (FSM)**: Collects detailed client requirements and reference files/attachments.
- 📦 **Order Tracking (`/myorders`)**: Real-time status for customers (*Pending*, *In Progress*, *Completed*, *Cancelled*).
- ⚡ **Admin Dashboard (`/admin`)**:
  - Instant alerts for new orders with one-click status action buttons (`[In Progress]`, `[Complete]`, `[Cancel]`).
  - Add, edit, or delete services directly from Telegram.
  - Broadcast announcements/discounts to all registered users.
  - View revenue & order analytics.
- 💾 **Asynchronous Database**: SQLite with `aiosqlite` ensures zero lag and high concurrency.

---

## 🛠️ Quick Setup Guide

### Step 1: Get your Bot Token from Telegram
1. Open Telegram and search for **`@BotFather`**.
2. Send `/newbot` and choose a display name and username for your bot.
3. Copy the **HTTP API Token** provided.

### Step 2: Get your Admin Telegram ID
1. Search for **`@userinfobot`** or **`@raw_data_bot`** on Telegram.
2. Send any message to get your numerical **User ID** (e.g., `123456789`).

### Step 3: Configure `.env`
Open the `.env` file in this directory and replace:
```env
BOT_TOKEN=your_actual_bot_token_from_botfather
ADMIN_IDS=your_telegram_numeric_id
DB_PATH=bot_database.db
```

### Step 4: Run the Bot
In your terminal / command prompt, run:
```bash
python bot.py
```

---

## 📂 Project Structure

```
├── bot.py                  # Main entry point & polling loop
├── config.py               # Loads environment settings
├── requirements.txt        # Dependencies (aiogram, aiosqlite, python-dotenv)
├── .env                    # Secret configuration (Token, Admin ID)
├── database/
│   ├── __init__.py
│   └── db.py               # SQLite tables & query handlers
├── handlers/
│   ├── __init__.py
│   ├── user.py             # User commands (/start, /services, /myorders, /about)
│   ├── order_fsm.py        # Multi-step order intake & admin alert dispatcher
│   └── admin.py            # Admin console (/admin, stats, add service, broadcast)
├── keyboards/
│   ├── __init__.py
│   ├── inline.py           # Inline buttons & menus
│   └── reply.py            # Bottom persistent keyboard
└── states/
    ├── __init__.py
    └── order_states.py     # Finite State Machine state definitions
```

---

## 📱 Bot Commands

| Command | Description |
| :--- | :--- |
| `/start` | Open the main menu & register user |
| `/services` | Browse available services catalog |
| `/myorders` | Check status of active & past orders |
| `/about` | View FAQ & order guidelines |
| `/support` | Get support contact details |
| `/admin` | Open Admin Control Panel (Admins only) |
