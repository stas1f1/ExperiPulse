#!/usr/bin/env python3
"""
Basic usage example for ExperimentBot

This example shows how to:
1. Set up the bot with your API key
2. Send simple notifications
3. Include metadata with notifications
4. Handle errors gracefully
"""

import os
import time
import sys

# Add the client library to the path
sys.path.insert(0, '../client')

from experiment_bot import ExperimentBot, setup

def main():
    print("🤖 ExperimentBot Basic Usage Example")
    print("=" * 50)

    # Check if API key is available
    api_key = os.getenv('EXPERIMENT_BOT_KEY')
    if not api_key:
        print("❌ No API key found!")
        print("\nTo get started:")
        setup()
        return

    # Initialize the bot
    try:
        bot = ExperimentBot()
        print("✅ Bot initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize bot: {e}")
        return

    # Test connection
    print("\n🔍 Testing connection...")
    if bot.validate_connection():
        print("✅ Connection successful!")
    else:
        print("❌ Connection failed. Make sure your API server is running.")
        return

    # Send a simple notification
    print("\n📤 Sending basic notification...")
    success = bot.notify("Hello from ExperimentBot! 🚀")
    print(f"{'✅' if success else '❌'} Basic notification: {'sent' if success else 'failed'}")

    # Send notification with metadata
    print("\n📤 Sending notification with metadata...")
    success = bot.notify(
        "Training started for model XYZ",
        model="ResNet50",
        dataset="ImageNet",
        batch_size=32,
        learning_rate=0.001
    )
    print(f"{'✅' if success else '❌'} Metadata notification: {'sent' if success else 'failed'}")

    # Simulate a long-running process
    print("\n⏱️  Simulating long-running process...")
    bot.notify("Starting long experiment...")

    for i in range(5):
        time.sleep(1)
        bot.notify(f"Progress update: Step {i+1}/5 completed")

    bot.notify("✅ Experiment completed successfully!")

    # Send heartbeat
    print("\n💓 Sending heartbeat...")
    success = bot.heartbeat()
    print(f"{'✅' if success else '❌'} Heartbeat: {'sent' if success else 'failed'}")

    print("\n🎉 Example completed!")

if __name__ == "__main__":
    main()