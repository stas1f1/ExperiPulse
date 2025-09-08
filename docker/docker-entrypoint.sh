#!/bin/bash
set -e

echo "🤖 Starting ExperimentBot Container..."

# Check for required environment variable
if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
    echo "❌ Error: TELEGRAM_BOT_TOKEN environment variable is required"
    echo "Set it with: docker run -e TELEGRAM_BOT_TOKEN=your_token_here ..."
    exit 1
fi

# Initialize database
echo "📄 Initializing database..."
python server/database.py

# Function to start the Telegram bot
start_bot() {
    echo "🚀 Starting Telegram bot..."
    python start_bot.py
}

# Function to start the API server
start_server() {
    echo "🌐 Starting API server..."
    python start_server.py
}

# Start both services in the background
start_bot &
BOT_PID=$!

start_server &
SERVER_PID=$!

echo "✅ ExperimentBot started successfully!"
echo "📱 Bot PID: $BOT_PID"
echo "🌐 Server PID: $SERVER_PID"
echo "📊 API docs available at http://localhost:8000/docs"
echo ""
echo "To get your API key:"
echo "1. Message your bot on Telegram"
echo "2. Send /start command"
echo ""

# Function to handle shutdown
shutdown() {
    echo "🛑 Shutting down ExperimentBot..."
    kill $BOT_PID $SERVER_PID
    wait $BOT_PID $SERVER_PID
    echo "👋 ExperimentBot stopped"
    exit 0
}

# Set up signal handlers
trap shutdown SIGTERM SIGINT

# Wait for both processes
wait $BOT_PID $SERVER_PID