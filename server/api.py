import os
import sqlite3
import json
from datetime import datetime
from typing import Optional
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer
from pydantic import BaseModel
import requests
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="ExperimentBot API", version="1.0.0")
security = HTTPBearer()

class NotificationRequest(BaseModel):
    message: str
    metadata: Optional[dict] = None

class ApiResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None

class APIServer:
    def __init__(self):
        self.db_path = os.getenv('DATABASE_PATH', 'experiment_bot.db')
        self.telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not self.telegram_token:
            raise ValueError("TELEGRAM_BOT_TOKEN not found in environment variables")

    def get_user_by_api_key(self, api_key: str) -> Optional[dict]:
        """Get user info by API key"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT user_id, chat_id, last_active FROM users WHERE api_key = ?",
                (api_key,)
            )
            result = cursor.fetchone()

            if result:
                user_id, chat_id, last_active = result
                # Update last_active
                cursor.execute(
                    "UPDATE users SET last_active = ? WHERE api_key = ?",
                    (datetime.now(), api_key)
                )
                conn.commit()

                return {
                    "user_id": user_id,
                    "chat_id": chat_id,
                    "last_active": last_active
                }
            return None

    async def send_telegram_message(self, chat_id: int, message: str) -> bool:
        """Send message via Telegram Bot API"""
        url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"

        # Format message with markdown
        formatted_message = f"🔬 **Experiment Notification**\n\n{message}"

        payload = {
            "chat_id": chat_id,
            "text": formatted_message,
            "parse_mode": "Markdown"
        }

        try:
            response = requests.post(url, json=payload, timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"Error sending Telegram message: {e}")
            return False

    def log_notification(self, user_id: int, message: str, metadata: dict = None, status: str = "sent"):
        """Log notification to database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO notifications (user_id, message, metadata, status) VALUES (?, ?, ?, ?)",
                (user_id, message, json.dumps(metadata) if metadata else None, status)
            )
            conn.commit()

api_server = APIServer()

async def get_current_user(token: str = Depends(security)):
    """Dependency to validate API key and get user"""
    api_key = token.credentials
    user = api_server.get_user_by_api_key(api_key)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user

@app.get("/", response_model=ApiResponse)
async def root():
    """Health check endpoint"""
    return ApiResponse(
        success=True,
        message="ExperimentBot API is running",
        data={"version": "1.0.0"}
    )

@app.post("/api/notify", response_model=ApiResponse)
async def send_notification(
    request: NotificationRequest,
    user: dict = Depends(get_current_user)
):
    """Send notification to user's Telegram chat"""
    try:
        # Send Telegram message
        success = await api_server.send_telegram_message(
            user["chat_id"],
            request.message
        )

        # Log notification
        api_server.log_notification(
            user["user_id"],
            request.message,
            request.metadata,
            "sent" if success else "failed"
        )

        if success:
            return ApiResponse(
                success=True,
                message="Notification sent successfully"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send Telegram message"
            )

    except Exception as e:
        api_server.log_notification(
            user["user_id"],
            request.message,
            request.metadata,
            "error"
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error sending notification: {str(e)}"
        )

@app.get("/api/validate", response_model=ApiResponse)
async def validate_key(user: dict = Depends(get_current_user)):
    """Validate API key and return user info"""
    return ApiResponse(
        success=True,
        message="API key is valid",
        data={
            "user_id": user["user_id"],
            "last_active": user["last_active"]
        }
    )

@app.post("/api/heartbeat", response_model=ApiResponse)
async def heartbeat(user: dict = Depends(get_current_user)):
    """Keep-alive endpoint for long-running processes"""
    return ApiResponse(
        success=True,
        message="Heartbeat received"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=os.getenv("API_HOST", "0.0.0.0"),
        port=int(os.getenv("API_PORT", "8000"))
    )