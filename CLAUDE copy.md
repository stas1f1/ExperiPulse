# Telegram Experiment Notification Bot - Development Instructions

## Project Overview

Build a Python library and Telegram bot system for sending notifications from experiments and long-running processes. The system should provide automatic key generation, process tracking, and rich notification capabilities.

## System Components

1. **Telegram Bot** - Handles user registration and message delivery
2. **Backend API Server** - Manages authentication and message routing
3. **Python Client Library** - User-facing library for sending notifications
4. **Database** - Stores user mappings and message history

## Development Instructions

### Phase 1: Project Setup and Structure

Create the following project structure:

```
experiment-notify/
├── bot/
│   ├── __init__.py
│   ├── telegram_bot.py
│   ├── handlers.py
│   └── config.py
├── backend/
│   ├── __init__.py
│   ├── app.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   └── auth.py
│   ├── database/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   └── connection.py
│   └── utils/
│       ├── __init__.py
│       └── key_generator.py
├── client/
│   ├── setup.py
│   ├── experiment_notify/
│   │   ├── __init__.py
│   │   ├── client.py
│   │   ├── tracker.py
│   │   ├── decorators.py
│   │   ├── metadata.py
│   │   └── exceptions.py
├── tests/
│   ├── test_bot.py
│   ├── test_backend.py
│   └── test_client.py
├── examples/
│   ├── basic_usage.py
│   ├── parallel_processes.py
│   └── ml_training_example.py
├── docker/
│   ├── Dockerfile.bot
│   ├── Dockerfile.backend
│   └── docker-compose.yml
├── requirements/
│   ├── base.txt
│   ├── bot.txt
│   ├── backend.txt
│   └── client.txt
├── .env.example
├── README.md
└── pyproject.toml
```

### Phase 2: Telegram Bot Implementation

#### File: `bot/config.py`

```python
import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class BotConfig:
    token: str
    backend_url: str
    admin_chat_id: Optional[int] = None
    max_message_length: int = 4096
    rate_limit: int = 30  # messages per minute
    
    @classmethod
    def from_env(cls):
        return cls(
            token=os.environ["TELEGRAM_BOT_TOKEN"],
            backend_url=os.environ.get("BACKEND_URL", "http://localhost:8000"),
            admin_chat_id=os.environ.get("ADMIN_CHAT_ID"),
            max_message_length=int(os.environ.get("MAX_MESSAGE_LENGTH", 4096)),
            rate_limit=int(os.environ.get("RATE_LIMIT", 30))
        )
```

#### File: `bot/handlers.py`

```python
import hashlib
import secrets
from datetime import datetime
from telegram import Update, ParseMode, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
import aiohttp
import json

class BotHandlers:
    def __init__(self, config, backend_client):
        self.config = config
        self.backend = backend_client
        
    async def start_command(self, update: Update, context: CallbackContext):
        """Generate a new API key for the user"""
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id
        username = update.effective_user.username
        
        # Generate secure API key
        api_key = f"exp_{secrets.token_urlsafe(32)}"
        
        # Register with backend
        response = await self.backend.register_user(
            telegram_user_id=user_id,
            chat_id=chat_id,
            username=username,
            api_key=api_key
        )
        
        if response['success']:
            message = (
                f"🚀 *Welcome to Experiment Notify Bot!*\n\n"
                f"Your API key:\n"
                f"`{api_key}`\n\n"
                f"*Quick Setup:*\n"
                f"1. Install: `pip install experiment-notify`\n"
                f"2. Set environment variable:\n"
                f"   `export EXPERIMENT_BOT_KEY={api_key}`\n"
                f"3. In your Python code:\n"
                f"```python\n"
                f"from experiment_notify import bot\n"
                f"bot.notify('Experiment started!')\n"
                f"```\n\n"
                f"Use /help for more commands"
            )
        else:
            # User already exists, retrieve existing key
            existing_key = response.get('api_key')
            message = (
                f"🔑 *You already have an API key:*\n"
                f"`{existing_key}`\n\n"
                f"Use /revoke to generate a new one\n"
                f"Use /help for more commands"
            )
            
        await update.message.reply_text(
            message, 
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True
        )
    
    async def help_command(self, update: Update, context: CallbackContext):
        """Show available commands and usage examples"""
        help_text = """
*Available Commands:*
/start - Generate or view your API key
/revoke - Revoke current key and generate new one
/status - Check your connection status
/stats - View your usage statistics
/mute - Temporarily mute notifications
/unmute - Resume notifications
/help - Show this help message

*Python Usage Examples:*

```python
# Basic notification
bot.notify("Training completed!")

# With metadata
bot.notify(
    "Epoch 10/100", 
    metrics={"loss": 0.23, "acc": 0.95}
)

# Track a function
@bot.track
def train_model():
    # Auto notifications on start/end
    pass

# Track a code block
with bot.track("Data processing"):
    process_data()
```

*Features:*
• Automatic process tracking
• Error notifications with stack traces  
• Parallel process management
• Progress tracking
• System metrics collection

[Documentation](https://github.com/yourusername/experiment-notify)
"""
        await update.message.reply_text(
            help_text,
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True
        )
    
    async def revoke_command(self, update: Update, context: CallbackContext):
        """Revoke current API key and generate a new one"""
        user_id = update.effective_user.id
        
        # Revoke old key in backend
        await self.backend.revoke_key(user_id)
        
        # Generate new key
        await self.start_command(update, context)
    
    async def status_command(self, update: Update, context: CallbackContext):
        """Check user's connection status"""
        user_id = update.effective_user.id
        
        status = await self.backend.get_user_status(user_id)
        
        if status:
            message = (
                f"✅ *Status: Active*\n\n"
                f"API Key: `{status['api_key'][:20]}...`\n"
                f"Created: {status['created_at']}\n"
                f"Last Active: {status['last_active']}\n"
                f"Messages Sent: {status['message_count']}\n"
                f"Active Processes: {status['active_processes']}"
            )
        else:
            message = "❌ No active API key found. Use /start to generate one."
            
        await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
```

#### File: `bot/telegram_bot.py`

```python
import asyncio
import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from handlers import BotHandlers
from config import BotConfig
import aiohttp

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ExperimentBot:
    def __init__(self):
        self.config = BotConfig.from_env()
        self.app = Application.builder().token(self.config.token).build()
        self.backend_client = BackendClient(self.config.backend_url)
        self.handlers = BotHandlers(self.config, self.backend_client)
        
        self.setup_handlers()
        
    def setup_handlers(self):
        """Register command handlers"""
        self.app.add_handler(CommandHandler("start", self.handlers.start_command))
        self.app.add_handler(CommandHandler("help", self.handlers.help_command))
        self.app.add_handler(CommandHandler("revoke", self.handlers.revoke_command))
        self.app.add_handler(CommandHandler("status", self.handlers.status_command))
        self.app.add_handler(CommandHandler("stats", self.handlers.stats_command))
        self.app.add_handler(CommandHandler("mute", self.handlers.mute_command))
        self.app.add_handler(CommandHandler("unmute", self.handlers.unmute_command))
        
    async def send_notification(self, chat_id: int, message: str, **kwargs):
        """Send a notification to a specific chat"""
        try:
            # Format message with metadata
            formatted_message = self.format_message(message, kwargs)
            
            # Split long messages
            if len(formatted_message) > self.config.max_message_length:
                messages = self.split_message(formatted_message)
                for msg in messages:
                    await self.app.bot.send_message(
                        chat_id=chat_id,
                        text=msg,
                        parse_mode=ParseMode.MARKDOWN
                    )
            else:
                await self.app.bot.send_message(
                    chat_id=chat_id,
                    text=formatted_message,
                    parse_mode=ParseMode.MARKDOWN
                )
                
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")
            
    def format_message(self, message: str, metadata: dict) -> str:
        """Format message with metadata"""
        formatted = message
        
        if metadata.get('process_name'):
            formatted = f"📊 *{metadata['process_name']}*\n{formatted}"
            
        if metadata.get('status'):
            status_emoji = {
                'started': '🚀',
                'running': '⚡',
                'completed': '✅',
                'error': '❌',
                'warning': '⚠️'
            }
            emoji = status_emoji.get(metadata['status'], '📌')
            formatted = f"{emoji} {formatted}"
            
        if metadata.get('metrics'):
            metrics_str = '\n'.join([
                f"• {k}: {v}" for k, v in metadata['metrics'].items()
            ])
            formatted = f"{formatted}\n\n*Metrics:*\n{metrics_str}"
            
        if metadata.get('error'):
            formatted = f"{formatted}\n\n*Error:*\n```\n{metadata['error'][:500]}\n```"
            
        return formatted
        
    def run(self):
        """Start the bot"""
        logger.info("Starting Experiment Notify Bot...")
        self.app.run_polling()

class BackendClient:
    """Client for communicating with backend API"""
    
    def __init__(self, backend_url):
        self.backend_url = backend_url
        
    async def register_user(self, telegram_user_id, chat_id, username, api_key):
        """Register a new user with the backend"""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.backend_url}/api/register",
                json={
                    "telegram_user_id": telegram_user_id,
                    "chat_id": chat_id,
                    "username": username,
                    "api_key": api_key
                }
            ) as resp:
                return await resp.json()

if __name__ == "__main__":
    bot = ExperimentBot()
    bot.run()
```

### Phase 3: Backend API Implementation

#### File: `backend/database/models.py`

```python
from sqlalchemy import Column, Integer, String, DateTime, JSON, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    telegram_user_id = Column(Integer, unique=True, index=True)
    chat_id = Column(Integer)
    username = Column(String, nullable=True)
    api_key = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=func.now())
    last_active = Column(DateTime, default=func.now())
    is_active = Column(Boolean, default=True)
    is_muted = Column(Boolean, default=False)
    message_count = Column(Integer, default=0)
    
class Process(Base):
    __tablename__ = "processes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    process_uuid = Column(String, unique=True, index=True)
    name = Column(String)
    status = Column(String)  # started, running, completed, error
    started_at = Column(DateTime, default=func.now())
    ended_at = Column(DateTime, nullable=True)
    metadata = Column(JSON)
    parent_process_id = Column(Integer, nullable=True)
    
class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    process_id = Column(Integer, nullable=True, index=True)
    message = Column(String)
    metadata = Column(JSON)
    created_at = Column(DateTime, default=func.now())
    delivered = Column(Boolean, default=False)
    delivered_at = Column(DateTime, nullable=True)
```

#### File: `backend/app.py`

```python
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uvicorn
import aiohttp
import asyncio
from datetime import datetime, timedelta
import logging

from database.connection import get_db, init_db
from database.models import User, Process, Notification
from utils.key_generator import validate_api_key
from api.routes import router as api_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Experiment Notify Backend")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api")

# Models
class RegisterRequest(BaseModel):
    telegram_user_id: int
    chat_id: int
    username: Optional[str]
    api_key: str

class NotifyRequest(BaseModel):
    message: str
    process_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = {}
    
class ProcessStartRequest(BaseModel):
    process_id: str
    name: str
    metadata: Optional[Dict[str, Any]] = {}
    parent_process_id: Optional[str] = None

# Background task queue
notification_queue = asyncio.Queue()

async def notification_worker():
    """Background worker to send notifications to Telegram bot"""
    bot_url = os.environ.get("BOT_INTERNAL_URL", "http://bot:5000")
    
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                notification = await notification_queue.get()
                
                # Send to Telegram bot service
                async with session.post(
                    f"{bot_url}/send_notification",
                    json=notification
                ) as resp:
                    if resp.status == 200:
                        # Mark as delivered in database
                        async with get_db() as db:
                            notif = db.query(Notification).filter_by(
                                id=notification['notification_id']
                            ).first()
                            if notif:
                                notif.delivered = True
                                notif.delivered_at = datetime.utcnow()
                                db.commit()
                    else:
                        logger.error(f"Failed to send notification: {resp.status}")
                        
            except Exception as e:
                logger.error(f"Notification worker error: {e}")
                await asyncio.sleep(5)

@app.on_event("startup")
async def startup_event():
    """Initialize database and start background workers"""
    init_db()
    asyncio.create_task(notification_worker())
    logger.info("Backend API started")

@app.post("/api/register")
async def register_user(request: RegisterRequest, db=Depends(get_db)):
    """Register a new user or return existing"""
    # Check if user exists
    existing_user = db.query(User).filter_by(
        telegram_user_id=request.telegram_user_id
    ).first()
    
    if existing_user:
        return {
            "success": False,
            "message": "User already exists",
            "api_key": existing_user.api_key
        }
    
    # Create new user
    new_user = User(
        telegram_user_id=request.telegram_user_id,
        chat_id=request.chat_id,
        username=request.username,
        api_key=request.api_key
    )
    db.add(new_user)
    db.commit()
    
    return {
        "success": True,
        "message": "User registered successfully",
        "api_key": request.api_key
    }

@app.post("/api/notify")
async def send_notification(
    request: NotifyRequest,
    api_key: str = Header(..., alias="X-API-Key"),
    db=Depends(get_db)
):
    """Send a notification to the user's Telegram"""
    # Validate API key
    user = db.query(User).filter_by(api_key=api_key, is_active=True).first()
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    if user.is_muted:
        return {"success": True, "message": "User is muted, notification skipped"}
    
    # Create notification record
    notification = Notification(
        user_id=user.id,
        message=request.message,
        metadata=request.metadata
    )
    db.add(notification)
    db.commit()
    
    # Update user last active
    user.last_active = datetime.utcnow()
    user.message_count += 1
    db.commit()
    
    # Add to notification queue
    await notification_queue.put({
        "notification_id": notification.id,
        "chat_id": user.chat_id,
        "message": request.message,
        "metadata": request.metadata
    })
    
    return {"success": True, "message": "Notification queued"}

@app.post("/api/process/start")
async def start_process(
    request: ProcessStartRequest,
    api_key: str = Header(..., alias="X-API-Key"),
    db=Depends(get_db)
):
    """Register a new process start"""
    user = db.query(User).filter_by(api_key=api_key, is_active=True).first()
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    # Create process record
    process = Process(
        user_id=user.id,
        process_uuid=request.process_id,
        name=request.name,
        status="started",
        metadata=request.metadata
    )
    db.add(process)
    db.commit()
    
    # Send notification
    await notification_queue.put({
        "chat_id": user.chat_id,
        "message": f"Process started: {request.name}",
        "metadata": {
            "process_id": request.process_id,
            "status": "started",
            **request.metadata
        }
    })
    
    return {"success": True, "process_id": request.process_id}

@app.post("/api/process/end")
async def end_process(
    process_id: str,
    status: str = "completed",
    metadata: Optional[Dict] = None,
    api_key: str = Header(..., alias="X-API-Key"),
    db=Depends(get_db)
):
    """Mark a process as ended"""
    user = db.query(User).filter_by(api_key=api_key, is_active=True).first()
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    process = db.query(Process).filter_by(
        process_uuid=process_id,
        user_id=user.id
    ).first()
    
    if not process:
        raise HTTPException(status_code=404, detail="Process not found")
    
    # Update process
    process.status = status
    process.ended_at = datetime.utcnow()
    if metadata:
        process.metadata = {**process.metadata, **metadata}
    db.commit()
    
    # Calculate duration
    duration = (process.ended_at - process.started_at).total_seconds()
    
    # Send notification
    await notification_queue.put({
        "chat_id": user.chat_id,
        "message": f"Process {'completed' if status == 'completed' else 'failed'}: {process.name}",
        "metadata": {
            "process_id": process_id,
            "status": status,
            "duration_seconds": duration,
            **(metadata or {})
        }
    })
    
    return {"success": True, "duration": duration}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### Phase 4: Python Client Library Implementation

#### File: `client/experiment_notify/__init__.py`

```python
import os
from .client import ExperimentNotifyClient

# Global client instance
bot = ExperimentNotifyClient()

# Export main components
from .tracker import track, track_progress
from .decorators import monitor

__all__ = ['bot', 'track', 'track_progress', 'monitor', 'ExperimentNotifyClient']
```

#### File: `client/experiment_notify/client.py`

```python
import os
import requests
import json
import uuid
from typing import Optional, Dict, Any
from datetime import datetime
import logging

from .exceptions import NotConfiguredError, APIError
from .metadata import collect_metadata

logger = logging.getLogger(__name__)

class ExperimentNotifyClient:
    """Main client for sending notifications to Telegram"""
    
    def __init__(self, api_key: Optional[str] = None, backend_url: Optional[str] = None):
        self.api_key = api_key or os.environ.get('EXPERIMENT_BOT_KEY')
        self.backend_url = backend_url or os.environ.get(
            'EXPERIMENT_BACKEND_URL', 
            'https://api.experiment-notify.com'
        )
        
        if not self.api_key:
            logger.warning("No API key configured. Set EXPERIMENT_BOT_KEY environment variable.")
            
        self._session = requests.Session()
        self._session.headers.update({
            'X-API-Key': self.api_key,
            'Content-Type': 'application/json'
        })
        
    def notify(
        self, 
        message: str, 
        **kwargs: Any
    ) -> bool:
        """
        Send a notification to Telegram
        
        Args:
            message: The notification message
            **kwargs: Additional metadata (metrics, tags, etc.)
            
        Returns:
            bool: True if notification was sent successfully
            
        Examples:
            >>> bot.notify("Training started")
            >>> bot.notify("Epoch 1/10", loss=0.5, accuracy=0.92)
            >>> bot.notify("Error occurred", error=str(e), severity="high")
        """
        if not self.api_key:
            raise NotConfiguredError("API key not configured")
            
        # Collect automatic metadata
        metadata = collect_metadata()
        metadata.update(kwargs)
        
        try:
            response = self._session.post(
                f"{self.backend_url}/api/notify",
                json={
                    "message": message,
                    "metadata": metadata
                }
            )
            response.raise_for_status()
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send notification: {e}")
            return False
            
    def start_process(
        self, 
        name: str, 
        process_id: Optional[str] = None,
        **metadata
    ) -> str:
        """Start tracking a process"""
        if not process_id:
            process_id = str(uuid.uuid4())
            
        try:
            response = self._session.post(
                f"{self.backend_url}/api/process/start",
                json={
                    "process_id": process_id,
                    "name": name,
                    "metadata": {**collect_metadata(), **metadata}
                }
            )
            response.raise_for_status()
            return process_id
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to start process: {e}")
            return process_id
            
    def end_process(
        self, 
        process_id: str, 
        status: str = "completed",
        **metadata
    ) -> bool:
        """End tracking a process"""
        try:
            response = self._session.post(
                f"{self.backend_url}/api/process/end",
                json={
                    "process_id": process_id,
                    "status": status,
                    "metadata": metadata
                }
            )
            response.raise_for_status()
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to end process: {e}")
            return False
            
    def heartbeat(self, process_id: str, **metadata) -> bool:
        """Send a heartbeat for a long-running process"""
        try:
            response = self._session.post(
                f"{self.backend_url}/api/process/heartbeat",
                json={
                    "process_id": process_id,
                    "metadata": metadata
                }
            )
            response.raise_for_status()
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send heartbeat: {e}")
            return False
```

#### File: `client/experiment_notify/tracker.py`

```python
import time
import uuid
import traceback
from contextlib import contextmanager
from typing import Optional, Any, Iterator, Union, Callable
import functools
from tqdm import tqdm

from .client import ExperimentNotifyClient
from .metadata import collect_system_metrics

class ProcessTracker:
    """Track and notify about process execution"""
    
    def __init__(
        self, 
        client: ExperimentNotifyClient,
        name: Optional[str] = None,
        notify_start: bool = True,
        notify_end: bool = True,
        notify_error: bool = True,
        include_metrics: bool = True
    ):
        self.client = client
        self.name = name or self._infer_name()
        self.process_id = str(uuid.uuid4())
        self.notify_start = notify_start
        self.notify_end = notify_end
        self.notify_error = notify_error
        self.include_metrics = include_metrics
        self.start_time = None
        
    def _infer_name(self) -> str:
        """Infer process name from call stack"""
        import inspect
        frame = inspect.currentframe()
        caller_frame = frame.f_back.f_back if frame else None
        if caller_frame:
            return f"{caller_frame.f_code.co_filename}:{caller_frame.f_code.co_name}"
        return "Unnamed Process"
        
    def __enter__(self):
        self.start_time = time.time()
        
        if self.notify_start:
            metrics = collect_system_metrics() if self.include_metrics else {}
            self.client.start_process(
                name=self.name,
                process_id=self.process_id,
                **metrics
            )
            
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        
        if exc_type:
            # Error occurred
            if self.notify_error:
                error_msg = ''.join(traceback.format_exception(exc_type, exc_val, exc_tb))
                # Truncate error message
                error_msg = error_msg[-2000:] if len(error_msg) > 2000 else error_msg
                
                self.client.end_process(
                    process_id=self.process_id,
                    status="error",
                    duration=duration,
                    error=error_msg,
                    error_type=exc_type.__name__
                )
        else:
            # Successful completion
            if self.notify_end:
                metrics = collect_system_metrics() if self.include_metrics else {}
                self.client.end_process(
                    process_id=self.process_id,
                    status="completed",
                    duration=duration,
                    **metrics
                )
                
        return False  # Don't suppress exceptions

@contextmanager
def track(
    name: Optional[str] = None,
    client: Optional[ExperimentNotifyClient] = None,
    **kwargs
):
    """
    Context manager for tracking code blocks
    
    Examples:
        >>> with track("Data preprocessing"):
        ...     process_data()
        
        >>> with track("Model training", notify_start=False):
        ...     train_model()
    """
    if client is None:
        from . import bot
        client = bot
        
    with ProcessTracker(client, name, **kwargs) as tracker:
        yield tracker

def track_progress(
    iterable,
    name: Optional[str] = None,
    client: Optional[ExperimentNotifyClient] = None,
    update_interval: Union[int, float] = 0.1,
    **tqdm_kwargs
):
    """
    Track progress of an iterable with periodic notifications
    
    Args:
        iterable: The iterable to track
        name: Process name
        client: ExperimentNotifyClient instance
        update_interval: How often to send updates (0-1 for percentage, >1 for iterations)
        **tqdm_kwargs: Additional arguments for tqdm
        
    Examples:
        >>> for epoch in track_progress(range(100), name="Training"):
        ...     train_epoch(epoch)
    """
    if client is None:
        from . import bot
        client = bot
        
    total = len(iterable) if hasattr(iterable, '__len__') else None
    name = name or "Progress"
    
    with track(name, client) as tracker:
        last_update = 0
        
        # Wrap with tqdm for local progress
        pbar = tqdm(iterable, desc=name, **tqdm_kwargs)
        
        for i, item in enumerate(pbar):
            # Determine if we should send an update
            should_update = False
            
            if update_interval <= 1.0 and total:
                # Percentage-based updates
                progress = (i + 1) / total
                if progress - last_update >= update_interval:
                    should_update = True
                    last_update = progress
            elif i % int(update_interval) == 0:
                # Iteration-based updates
                should_update = True
                
            if should_update:
                metrics = {
                    "iteration": i + 1,
                    "progress": f"{(i+1)/total*100:.1f}%" if total else str(i+1)
                }
                
                # Get metrics from tqdm if available
                if hasattr(pbar, 'format_dict'):
                    format_dict = pbar.format_dict
                    if 'rate' in format_dict and format_dict['rate']:
                        metrics['rate'] = f"{format_dict['rate']:.2f} it/s"
                    if 'elapsed' in format_dict:
                        metrics['elapsed'] = f"{format_dict['elapsed']:.1f}s"
                        
                client.notify(
                    f"Progress: {name}",
                    **metrics
                )
                
            yield item
```

#### File: `client/experiment_notify/decorators.py`

```python
import functools
import time
import traceback
from typing import Optional, Callable, Any

from .client import ExperimentNotifyClient
from .tracker import ProcessTracker

def monitor(
    _func: Optional[Callable] = None,
    *,
    name: Optional[str] = None,
    client: Optional[ExperimentNotifyClient] = None,
    notify_start: bool = True,
    notify_end: bool = True,
    notify_error: bool = True,
    include_args: bool = False,
    include_result: bool = False
):
    """
    Decorator to monitor function execution
    
    Examples:
        >>> @monitor
        ... def train_model(data):
        ...     return model.fit(data)
        
        >>> @monitor(name="Custom Training", include_result=True)
        ... def train():
        ...     return {"loss": 0.5}
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Get client
            nonlocal client
            if client is None:
                from . import bot
                client = bot
                
            # Determine process name
            process_name = name or f"{func.__module__}.{func.__name__}"
            
            # Prepare metadata
            metadata = {}
            if include_args:
                metadata['args'] = str(args)[:500]  # Truncate
                metadata['kwargs'] = str(kwargs)[:500]
                
            # Create tracker
            tracker = ProcessTracker(
                client=client,
                name=process_name,
                notify_start=notify_start,
                notify_end=notify_end,
                notify_error=notify_error
            )
            
            with tracker:
                result = func(*args, **kwargs)
                
                if include_result and notify_end:
                    result_str = str(result)[:500]  # Truncate
                    client.notify(
                        f"Result from {process_name}",
                        result=result_str
                    )
                    
                return result
                
        return wrapper
        
    if _func is None:
        return decorator
    else:
        return decorator(_func)
```

#### File: `client/experiment_notify/metadata.py`

```python
import os
import sys
import platform
import subprocess
import socket
import psutil
from typing import Dict, Any, Optional
import importlib.metadata

def collect_metadata() -> Dict[str, Any]:
    """Collect automatic metadata about the environment"""
    metadata = {}
    
    # Python info
    metadata['python_version'] = sys.version.split()[0]
    metadata['platform'] = platform.platform()
    
    # Hostname
    try:
        metadata['hostname'] = socket.gethostname()
    except:
        pass
    
    # Virtual environment
    if hasattr(sys, 'prefix'):
        metadata['venv'] = os.path.basename(sys.prefix)
    
    # Git info
    git_info = get_git_info()
    if git_info:
        metadata.update(git_info)
    
    # Key packages
    packages = get_installed_packages()
    if packages:
        metadata['packages'] = packages
    
    return metadata

def get_git_info() -> Optional[Dict[str, str]]:
    """Get current git commit and branch"""
    try:
        commit = subprocess.check_output(
            ['git', 'rev-parse', 'HEAD'],
            stderr=subprocess.DEVNULL
        ).decode('utf-8').strip()[:8]
        
        branch = subprocess.check_output(
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
            stderr=subprocess.DEVNULL
        ).decode('utf-8').strip()
        
        return {
            'git_commit': commit,
            'git_branch': branch
        }
    except:
        return None

def get_installed_packages() -> Dict[str, str]:
    """Get versions of key ML packages"""
    packages = {}
    important_packages = [
        'torch', 'tensorflow', 'numpy', 'pandas', 
        'scikit-learn', 'transformers', 'datasets'
    ]
    
    for pkg in important_packages:
        try:
            version = importlib.metadata.version(pkg)
            packages[pkg] = version
        except:
            pass
            
    return packages

def collect_system_metrics() -> Dict[str, Any]:
    """Collect system resource metrics"""
    metrics = {}
    
    try:
        # Memory
        mem = psutil.virtual_memory()
        metrics['memory_percent'] = mem.percent
        metrics['memory_used_gb'] = mem.used / (1024**3)
        
        # CPU
        metrics['cpu_percent'] = psutil.cpu_percent(interval=0.1)
        metrics['cpu_count'] = psutil.cpu_count()
        
        # Disk
        disk = psutil.disk_usage('/')
        metrics['disk_percent'] = disk.percent
        
        # GPU (if available)
        gpu_metrics = get_gpu_metrics()
        if gpu_metrics:
            metrics.update(gpu_metrics)
            
    except Exception as e:
        pass
        
    return metrics

def get_gpu_metrics() -> Optional[Dict[str, Any]]:
    """Get GPU metrics if available"""
    try:
        import pynvml
        pynvml.nvmlInit()
        
        metrics = {}
        device_count = pynvml.nvmlDeviceGetCount()
        
        for i in range(device_count):
            handle = pynvml.nvmlDeviceGetHandleByIndex(i)
            
            # Memory
            mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
            metrics[f'gpu_{i}_memory_percent'] = (mem_info.used / mem_info.total) * 100
            
            # Utilization
            util = pynvml.nvmlDeviceGetUtilizationRates(handle)
            metrics[f'gpu_{i}_utilization'] = util.gpu
            
            # Temperature
            temp = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
            metrics[f'gpu_{i}_temperature'] = temp
            
        return metrics
        
    except:
        return None
```

#### File: `client/setup.py`

```python
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="experiment-notify",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Send notifications from experiments to Telegram",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/experiment-notify",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.28.0",
        "psutil>=5.9.0",
        "tqdm>=4.65.0",
    ],
    extras_require={
        "gpu": ["pynvml>=11.5.0"],
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "experiment-notify-setup=experiment_notify.setup:main",
        ],
    },
)
```

### Phase 5: Docker and Deployment

#### File: `docker/docker-compose.yml`

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: experiment_notify
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  backend:
    build:
      context: ..
      dockerfile: docker/Dockerfile.backend
    environment:
      DATABASE_URL: postgresql://postgres:${DB_PASSWORD}@postgres:5432/experiment_notify
      REDIS_URL: redis://redis:6379
      BOT_INTERNAL_URL: http://bot:5000
      SECRET_KEY: ${SECRET_KEY}
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis
    volumes:
      - ../backend:/app

  bot:
    build:
      context: ..
      dockerfile: docker/Dockerfile.bot
    environment:
      TELEGRAM_BOT_TOKEN: ${TELEGRAM_BOT_TOKEN}
      BACKEND_URL: http://backend:8000
      DATABASE_URL: postgresql://postgres:${DB_PASSWORD}@postgres:5432/experiment_notify
    depends_on:
      - backend
      - postgres
    volumes:
      - ../bot:/app

volumes:
  postgres_data:
```

#### File: `docker/Dockerfile.backend`

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements/backend.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/ .

# Run the application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

### Phase 6: Testing

#### File: `tests/test_client.py`

```python
import pytest
from unittest.mock import Mock, patch, MagicMock
import os

from experiment_notify import ExperimentNotifyClient, track, monitor

@pytest.fixture
def client():
    """Create a test client"""
    return ExperimentNotifyClient(
        api_key="test_key_123",
        backend_url="http://localhost:8000"
    )

def test_notify_sends_request(client):
    """Test that notify sends correct request"""
    with patch('requests.Session.post') as mock_post:
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        result = client.notify("Test message", custom_field="value")
        
        assert result is True
        mock_post.assert_called_once()
        
        # Check request data
        call_args = mock_post.call_args
        json_data = call_args.kwargs['json']
        
        assert json_data['message'] == "Test message"
        assert 'metadata' in json_data
        assert json_data['metadata']['custom_field'] == "value"

def test_track_context_manager(client):
    """Test track context manager"""
    with patch.object(client, 'start_process') as mock_start:
        with patch.object(client, 'end_process') as mock_end:
            mock_start.return_value = "process_123"
            
            with track("Test Process", client=client) as tracker:
                assert tracker.process_id is not None
                
            mock_start.assert_called_once()
            mock_end.assert_called_once()
            
            # Check end was called with completed status
            end_call = mock_end.call_args
            assert end_call.kwargs['status'] == 'completed'

def test_track_context_manager_with_error(client):
    """Test track context manager handles errors"""
    with patch.object(client, 'start_process') as mock_start:
        with patch.object(client, 'end_process') as mock_end:
            mock_start.return_value = "process_123"
            
            with pytest.raises(ValueError):
                with track("Test Process", client=client):
                    raise ValueError("Test error")
                    
            # Check end was called with error status
            end_call = mock_end.call_args
            assert end_call.kwargs['status'] == 'error'
            assert 'error' in end_call.kwargs

def test_monitor_decorator(client):
    """Test monitor decorator"""
    with patch.object(client, 'start_process') as mock_start:
        with patch.object(client, 'end_process') as mock_end:
            mock_start.return_value = "process_123"
            
            @monitor(client=client)
            def test_function(x, y):
                return x + y
                
            result = test_function(2, 3)
            
            assert result == 5
            mock_start.assert_called_once()
            mock_end.assert_called_once()

def test_api_key_from_environment():
    """Test loading API key from environment"""
    with patch.dict(os.environ, {'EXPERIMENT_BOT_KEY': 'env_key_456'}):
        client = ExperimentNotifyClient()
        assert client.api_key == 'env_key_456'
```

### Phase 7: Examples

#### File: `examples/basic_usage.py`

```python
#!/usr/bin/env python3
"""
Basic usage examples for experiment-notify
"""

from experiment_notify import bot, track, monitor
import time
import random

# Example 1: Simple notification
def example_simple_notification():
    """Send a simple notification"""
    bot.notify("🚀 Experiment started!")
    time.sleep(1)
    bot.notify("✅ Experiment completed!")

# Example 2: Notification with metrics
def example_with_metrics():
    """Send notification with metrics"""
    for epoch in range(3):
        loss = random.random()
        accuracy = random.random()
        
        bot.notify(
            f"Epoch {epoch+1}/3 completed",
            loss=round(loss, 4),
            accuracy=round(accuracy, 4),
            learning_rate=0.001
        )
        time.sleep(1)

# Example 3: Using context manager
def example_context_manager():
    """Track a code block with context manager"""
    with track("Data preprocessing"):
        print("Loading data...")
        time.sleep(1)
        print("Cleaning data...")
        time.sleep(1)
        print("Done!")

# Example 4: Using decorator
@monitor(name="Model training")
def train_model(epochs=3):
    """Example function with monitor decorator"""
    for epoch in range(epochs):
        print(f"Training epoch {epoch+1}/{epochs}")
        time.sleep(1)
    return {"final_loss": 0.1234}

# Example 5: Error handling
def example_error_handling():
    """Show how errors are reported"""
    try:
        with track("Risky operation"):
            print("Starting risky operation...")
            time.sleep(1)
            raise ValueError("Something went wrong!")
    except ValueError:
        print("Error was reported to Telegram")

if __name__ == "__main__":
    print("Running examples...")
    
    print("\n1. Simple notification")
    example_simple_notification()
    
    print("\n2. With metrics")
    example_with_metrics()
    
    print("\n3. Context manager")
    example_context_manager()
    
    print("\n4. Decorator")
    result = train_model(epochs=2)
    print(f"Result: {result}")
    
    print("\n5. Error handling")
    example_error_handling()
    
    print("\nAll examples completed!")
```

### Phase 8: Configuration Files

#### File: `.env.example`

```bash
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_bot_token_here
ADMIN_CHAT_ID=your_admin_chat_id

# Database
DB_PASSWORD=secure_password_here
DATABASE_URL=postgresql://postgres:secure_password_here@localhost:5432/experiment_notify

# Backend API
SECRET_KEY=your_secret_key_here
BACKEND_URL=https://api.experiment-notify.com
BOT_INTERNAL_URL=http://bot:5000

# Redis (for caching and queues)
REDIS_URL=redis://localhost:6379

# Client defaults
EXPERIMENT_BOT_KEY=exp_your_api_key_here
EXPERIMENT_BACKEND_URL=http://localhost:8000
```

#### File: `requirements/base.txt`

```
pydantic>=2.0.0
python-dotenv>=1.0.0
httpx>=0.24.0
aiohttp>=3.8.0
```

#### File: `requirements/bot.txt`

```
-r base.txt
python-telegram-bot>=20.0
```

#### File: `requirements/backend.txt`

```
-r base.txt
fastapi>=0.100.0
uvicorn[standard]>=0.23.0
sqlalchemy>=2.0.0
alembic>=1.11.0
psycopg2-binary>=2.9.0
redis>=4.6.0
```

#### File: `requirements/client.txt`

```
requests>=2.28.0
psutil>=5.9.0
tqdm>=4.65.0
pynvml>=11.5.0  # Optional, for GPU metrics
```

### Deployment Instructions

1. **Initial Setup**
   ```bash
   # Clone repository
   git clone <repo-url>
   cd experiment-notify
   
   # Copy environment variables
   cp .env.example .env
   # Edit .env with your values
   
   # Install dependencies
   pip install -r requirements/backend.txt
   pip install -r requirements/bot.txt
   ```

2. **Create Telegram Bot**
   ```bash
   # 1. Message @BotFather on Telegram
   # 2. Send /newbot
   # 3. Choose name and username
   # 4. Copy token to .env
   ```

3. **Database Setup**
   ```bash
   # Start PostgreSQL
   docker-compose up -d postgres
   
   # Run migrations
   alembic init alembic
   alembic revision --autogenerate -m "Initial migration"
   alembic upgrade head
   ```

4. **Start Services**
   ```bash
   # Using Docker Compose
   docker-compose up -d
   
   # Or run individually
   python backend/app.py
   python bot/telegram_bot.py
   ```

5. **Install Client Library**
   ```bash
   cd client
   pip install -e .
   ```

6. **Test Installation**
   ```bash
   python examples/basic_usage.py
   ```

## Testing Checklist

- [ ] Bot responds to /start command
- [ ] API key generation works
- [ ] Backend accepts authenticated requests
- [ ] Notifications appear in Telegram
- [ ] Process tracking works (start/end)
- [ ] Error notifications include stack traces
- [ ] Metrics collection works
- [ ] Parallel processes are distinguished
- [ ] Rate limiting prevents spam
- [ ] Client handles network errors gracefully

## Production Deployment

1. **Use environment-specific configs**
2. **Set up SSL/TLS for API**
3. **Configure rate limiting**
4. **Set up monitoring (Prometheus/Grafana)**
5. **Configure log aggregation**
6. **Set up backup strategy for database**
7. **Use secrets management (Vault/AWS Secrets Manager)**
8. **Configure auto-scaling for API**
9. **Set up CI/CD pipeline**
10. **Create documentation site**

## Next Steps

After implementing the core system:

1. Add web dashboard for viewing history
2. Implement data visualization features
3. Add support for file attachments (plots, logs)
4. Create integrations (Weights&Biases, MLflow)
5. Add team/organization features
6. Implement alert rules and thresholds
7. Add support for other messaging platforms (Slack, Discord)
8. Create browser extension for Jupyter notebooks
9. Add voice message summaries for long reports
10. Implement experiment comparison features