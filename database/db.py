import aiosqlite
from datetime import datetime
from config import DB_PATH

class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path

    async def init_db(self):
        """Initialize tables and seed default services if none exist."""
        async with aiosqlite.connect(self.db_path) as db:
            # Enable foreign keys
            await db.execute("PRAGMA foreign_keys = ON;")

            # 1. Users table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    full_name TEXT,
                    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # 2. Services table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS services (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT NOT NULL,
                    price REAL NOT NULL,
                    duration TEXT NOT NULL,
                    is_active INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # 3. Orders table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    service_id INTEGER NOT NULL,
                    requirements TEXT NOT NULL,
                    attachment_file_id TEXT,
                    status TEXT DEFAULT 'Pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id),
                    FOREIGN KEY (service_id) REFERENCES services(id)
                );
            """)

            await db.commit()

            # Seed default services if empty
            async with db.execute("SELECT COUNT(*) FROM services") as cursor:
                count = (await cursor.fetchone())[0]
                if count == 0:
                    default_services = [
                        (
                            "🚀 Telegram Bot Development",
                            "Custom automated Telegram bot with database, payments, and admin panel.",
                            49.99,
                            "2-3 Days"
                        ),
                        (
                            "🌐 Modern Landing Page",
                            "Ultra-fast responsive portfolio / sales landing page with high conversion rate.",
                            79.99,
                            "3-4 Days"
                        ),
                        (
                            "🎨 Graphic & UI/UX Design",
                            "Professional banner, logo, or mobile UI/UX design kit.",
                            29.99,
                            "24-48 Hours"
                        ),
                        (
                            "📈 Social Media Marketing",
                            "1-Month growth strategy, targeted content calendar, and analytics audit.",
                            99.99,
                            "7 Days"
                        )
                    ]
                    await db.executemany(
                        "INSERT INTO services (name, description, price, duration) VALUES (?, ?, ?, ?)",
                        default_services
                    )
                    await db.commit()

    # User Methods
    async def add_or_update_user(self, user_id: int, username: str | None, full_name: str):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO users (user_id, username, full_name)
                VALUES (?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    username = excluded.username,
                    full_name = excluded.full_name
            """, (user_id, username, full_name))
            await db.commit()

    async def get_total_users_count(self) -> int:
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT COUNT(*) FROM users") as cursor:
                return (await cursor.fetchone())[0]

    async def get_all_user_ids(self) -> list[int]:
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT user_id FROM users") as cursor:
                rows = await cursor.fetchall()
                return [row[0] for row in rows]

    # Service Methods
    async def get_active_services(self) -> list[dict]:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM services WHERE is_active = 1 ORDER BY id ASC") as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

    async def get_all_services(self) -> list[dict]:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM services ORDER BY id DESC") as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

    async def get_service_by_id(self, service_id: int) -> dict | None:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM services WHERE id = ?", (service_id,)) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else None

    async def add_service(self, name: str, description: str, price: float, duration: str) -> int:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                INSERT INTO services (name, description, price, duration)
                VALUES (?, ?, ?, ?)
            """, (name, description, price, duration))
            await db.commit()
            return cursor.lastrowid

    async def delete_service(self, service_id: int):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("UPDATE services SET is_active = 0 WHERE id = ?", (service_id,))
            await db.commit()

    # Order Methods
    async def create_order(self, user_id: int, service_id: int, requirements: str, file_id: str | None = None) -> int:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                INSERT INTO orders (user_id, service_id, requirements, attachment_file_id, status)
                VALUES (?, ?, ?, ?, 'Pending')
            """, (user_id, service_id, requirements, file_id))
            await db.commit()
            return cursor.lastrowid

    async def get_order_by_id(self, order_id: int) -> dict | None:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            query = """
                SELECT o.*, s.name AS service_name, s.price, s.duration, u.username, u.full_name
                FROM orders o
                JOIN services s ON o.service_id = s.id
                JOIN users u ON o.user_id = u.user_id
                WHERE o.id = ?
            """
            async with db.execute(query, (order_id,)) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else None

    async def get_user_orders(self, user_id: int) -> list[dict]:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            query = """
                SELECT o.*, s.name AS service_name, s.price
                FROM orders o
                JOIN services s ON o.service_id = s.id
                WHERE o.user_id = ?
                ORDER BY o.id DESC
            """
            async with db.execute(query, (user_id,)) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

    async def get_recent_orders(self, limit: int = 10) -> list[dict]:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            query = """
                SELECT o.*, s.name AS service_name, s.price, u.username, u.full_name
                FROM orders o
                JOIN services s ON o.service_id = s.id
                JOIN users u ON o.user_id = u.user_id
                ORDER BY o.id DESC
                LIMIT ?
            """
            async with db.execute(query, (limit,)) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

    async def update_order_status(self, order_id: int, status: str):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("UPDATE orders SET status = ? WHERE id = ?", (status, order_id))
            await db.commit()

    async def get_stats(self) -> dict:
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT COUNT(*) FROM users") as c1:
                total_users = (await c1.fetchone())[0]
            async with db.execute("SELECT COUNT(*) FROM orders") as c2:
                total_orders = (await c2.fetchone())[0]
            async with db.execute("SELECT COUNT(*) FROM orders WHERE status = 'Completed'") as c3:
                completed_orders = (await c3.fetchone())[0]
            async with db.execute("""
                SELECT COALESCE(SUM(s.price), 0)
                FROM orders o
                JOIN services s ON o.service_id = s.id
                WHERE o.status = 'Completed'
            """) as c4:
                total_revenue = (await c4.fetchone())[0]

            return {
                "total_users": total_users,
                "total_orders": total_orders,
                "completed_orders": completed_orders,
                "total_revenue": total_revenue
            }

# Global DB instance
db = Database(DB_PATH)

async def init_db():
    await db.init_db()
