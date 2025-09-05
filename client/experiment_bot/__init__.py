import os
import requests
from typing import Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()

class ExperimentBot:
    """Simple client for sending experiment notifications via Telegram"""

    def __init__(self, api_key: Optional[str] = None, api_url: Optional[str] = None):
        """
        Initialize ExperimentBot client

        Args:
            api_key: API key for authentication. If None, loads from EXPERIMENT_BOT_KEY env var
            api_url: Base URL for the API. If None, loads from EXPERIMENT_BOT_API_URL or defaults to localhost
        """
        self.api_key = api_key or os.getenv('EXPERIMENT_BOT_KEY')
        if not self.api_key:
            raise ValueError(
                "API key is required. Set EXPERIMENT_BOT_KEY environment variable or pass api_key parameter."
            )

        self.api_url = api_url or os.getenv('EXPERIMENT_BOT_API_URL', 'http://localhost:8000')
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        })

    def notify(self, message: str, **metadata) -> bool:
        """
        Send a notification message

        Args:
            message: The notification message to send
            **metadata: Additional metadata to include with the notification

        Returns:
            bool: True if notification was sent successfully, False otherwise
        """
        try:
            payload = {
                'message': message,
                'metadata': metadata if metadata else None
            }

            response = self.session.post(
                f'{self.api_url}/api/notify',
                json=payload,
                timeout=10
            )

            if response.status_code == 200:
                return True
            else:
                print(f"Failed to send notification: {response.status_code} - {response.text}")
                return False

        except requests.RequestException as e:
            print(f"Error sending notification: {e}")
            return False

    def validate_connection(self) -> bool:
        """
        Validate API key and connection

        Returns:
            bool: True if connection is valid, False otherwise
        """
        try:
            response = self.session.get(
                f'{self.api_url}/api/validate',
                timeout=5
            )
            return response.status_code == 200

        except requests.RequestException as e:
            print(f"Connection validation failed: {e}")
            return False

    def heartbeat(self) -> bool:
        """
        Send heartbeat to keep connection alive

        Returns:
            bool: True if heartbeat was successful, False otherwise
        """
        try:
            response = self.session.post(
                f'{self.api_url}/api/heartbeat',
                timeout=5
            )
            return response.status_code == 200

        except requests.RequestException as e:
            print(f"Heartbeat failed: {e}")
            return False

# Create a default instance for convenience
try:
    bot = ExperimentBot()
except ValueError:
    # If no API key is available, bot will be None
    bot = None

def setup():
    """
    Interactive setup function to help users get started
    """
    print("🤖 ExperimentBot Setup")
    print("=" * 50)
    print("1. Create a Telegram bot by messaging @BotFather")
    print("2. Start your ExperimentBot server with your bot token")
    print("3. Message your bot with /start to get your API key")
    print("4. Set your API key as an environment variable:")
    print()
    print("   export EXPERIMENT_BOT_KEY=your_api_key_here")
    print()
    print("5. Test your connection:")
    print()
    print("   from experiment_bot import bot")
    print("   bot.notify('Hello from my experiment!')")
    print()

__all__ = ['ExperimentBot', 'bot', 'setup']