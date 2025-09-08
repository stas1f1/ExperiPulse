import os
import secrets
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from dotenv import load_dotenv
import sqlite3
from datetime import datetime

load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class ExperimentBot:
    def __init__(self):
        self.token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not self.token:
            raise ValueError("TELEGRAM_BOT_TOKEN not found in environment variables")

        self.db_path = os.getenv('DATABASE_PATH', 'experiment_bot.db')
        self.init_database()

    def init_database(self):
        """Initialize SQLite database with required tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    api_key TEXT UNIQUE NOT NULL,
                    chat_id INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS notifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    message TEXT NOT NULL,
                    metadata TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'sent',
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            conn.commit()

    def generate_api_key(self) -> str:
        """Generate a secure API key"""
        return f"exp_{secrets.token_urlsafe(16)}"

    def get_or_create_user(self, user_id: int, chat_id: int) -> str:
        """Get existing API key or create new user"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Check if user exists
            cursor.execute("SELECT api_key FROM users WHERE user_id = ?", (user_id,))
            result = cursor.fetchone()

            if result:
                # Update chat_id and last_active
                cursor.execute(
                    "UPDATE users SET chat_id = ?, last_active = ? WHERE user_id = ?",
                    (chat_id, datetime.now(), user_id)
                )
                return result[0]
            else:
                # Create new user
                api_key = self.generate_api_key()
                cursor.execute(
                    "INSERT INTO users (user_id, api_key, chat_id) VALUES (?, ?, ?)",
                    (user_id, api_key, chat_id)
                )
                conn.commit()
                return api_key

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user = update.effective_user
        chat_id = update.effective_chat.id

        api_key = self.get_or_create_user(user.id, chat_id)

        message = f"""
🤖 **ExperimentBot is ready!**

Your API key: `{api_key}`

**Quick setup:**
```bash
pip install requests python-dotenv
```

**Python usage:**
```python
import os
os.environ['EXPERIMENT_BOT_KEY'] = '{api_key}'

from experiment_bot import bot
bot.notify("Hello from my experiment!")
```

**Commands:**
/start - Get your API key
/revoke - Generate new API key
/status - Check connection status

Keep this key secure! 🔒
        """

        await update.message.reply_text(message, parse_mode='Markdown')

    async def revoke_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /revoke command"""
        user = update.effective_user
        chat_id = update.effective_chat.id

        # Generate new API key
        new_api_key = self.generate_api_key()

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET api_key = ?, last_active = ? WHERE user_id = ?",
                (new_api_key, datetime.now(), user.id)
            )
            conn.commit()

        message = f"""
🔄 **API Key Revoked**

Your new API key: `{new_api_key}`

Update your environment variable:
```bash
export EXPERIMENT_BOT_KEY={new_api_key}
```
        """

        await update.message.reply_text(message, parse_mode='Markdown')

    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command"""
        user = update.effective_user

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT api_key, created_at, last_active FROM users WHERE user_id = ?",
                (user.id,)
            )
            result = cursor.fetchone()

            if result:
                api_key, created_at, last_active = result
                message = f"""
📊 **Connection Status**

✅ **Active**
API Key: `{api_key[:10]}...`
Created: {created_at}
Last Active: {last_active}

Ready to receive notifications! 🚀
                """
            else:
                message = "❌ **Not registered**\n\nUse /start to get your API key."

        await update.message.reply_text(message, parse_mode='Markdown')

    def run(self):
        """Start the bot"""
        application = Application.builder().token(self.token).build()

        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(CommandHandler("revoke", self.revoke_command))
        application.add_handler(CommandHandler("status", self.status_command))

        logger.info("Starting ExperimentBot...")
        application.run_polling()

if __name__ == "__main__":
    bot = ExperimentBot()
    bot.run()