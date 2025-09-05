#!/bin/bash
# Quick activation script for ExperimentBot development

echo "🤖 Activating ExperimentBot environment..."
source experiment_bot_env/bin/activate

echo "✅ Virtual environment activated!"
echo "📍 Current directory: $(pwd)"
echo "🐍 Python: $(which python)"

echo ""
echo "Available commands:"
echo "  python start_bot.py     - Start Telegram bot"
echo "  python start_server.py  - Start API server"
echo "  python test_mvp.py      - Run test suite"
echo "  python examples/basic_usage.py - Run example"
echo ""

# Keep shell open in activated environment
bash