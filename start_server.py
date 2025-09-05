#!/usr/bin/env python3
"""
Start the API server

Usage:
    python start_server.py

Make sure to set TELEGRAM_BOT_TOKEN in your environment variables.
"""

import os
import sys
import uvicorn
from server.database import init_database

def main():
    print("🚀 Starting ExperimentBot API Server...")

    # Check for required environment variables
    if not os.getenv('TELEGRAM_BOT_TOKEN'):
        print("❌ Error: TELEGRAM_BOT_TOKEN environment variable not set")
        print("\nThis is needed for the API server to send Telegram messages.")
        print("Set it with: export TELEGRAM_BOT_TOKEN=your_token_here")
        sys.exit(1)

    # Initialize database
    print("📄 Initializing database...")
    init_database()

    # Get configuration
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))

    print(f"🌐 Server will run on http://{host}:{port}")
    print("📚 API docs available at http://localhost:8000/docs")

    # Start the server
    try:
        uvicorn.run(
            "server.api:app",
            host=host,
            port=port,
            reload=True,
            access_log=True
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()