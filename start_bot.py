#!/usr/bin/env python3
"""
Start the Telegram bot

Usage:
    python start_bot.py

Make sure to set TELEGRAM_BOT_TOKEN in your environment variables.
"""

import os
import sys
from bot.telegram_bot import ExperimentBot
from server.database import init_database

def main():
    print("🤖 Starting ExperimentBot...")

    # Check for required environment variables
    if not os.getenv('TELEGRAM_BOT_TOKEN'):
        print("❌ Error: TELEGRAM_BOT_TOKEN environment variable not set")
        print("\nTo get a bot token:")
        print("1. Message @BotFather on Telegram")
        print("2. Create a new bot with /newbot")
        print("3. Copy the token and set it as an environment variable:")
        print("   export TELEGRAM_BOT_TOKEN=your_token_here")
        sys.exit(1)

    # Initialize database
    print("📄 Initializing database...")
    init_database()

    # Start the bot
    try:
        bot = ExperimentBot()
        bot.run()
    except KeyboardInterrupt:
        print("\n👋 Bot stopped by user")
    except Exception as e:
        print(f"❌ Error starting bot: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()