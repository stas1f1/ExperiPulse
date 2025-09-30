# ExperiPulse

A Telegram bot that allows you to track your progress with long experiments and receive real-time notifications.

## 🚀 Quick Start

### Option 1: Docker (Recommended)

```bash
# Get bot token from @BotFather on Telegram
# Copy environment template and set your token
cp .env.docker .env
nano .env  # Set TELEGRAM_BOT_TOKEN=your_token_here

# Start with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f
```

### Option 2: Local Development

```bash
# Create virtual environment
python -m venv experiment_bot_env
source experiment_bot_env/bin/activate  # or use ./activate.sh

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export TELEGRAM_BOT_TOKEN=your_bot_token_here

# Start services (in separate terminals)
python start_bot.py
python start_server.py
```

## 📱 Usage

1. **Get your API key**: Message your bot with `/start`
2. **Set environment variable**: `export EXPERIMENT_BOT_KEY=your_api_key`
3. **Send notifications**:

```python
from experiment_bot import bot

# Simple notification
bot.notify("Training started! 🚀")

# With metadata
bot.notify(
    "Epoch 50/100 completed",
    accuracy=0.95,
    loss=0.03,
    model="ResNet50"
)
```

## 🐳 Docker

See [DOCKER.md](DOCKER.md) for complete Docker setup and deployment instructions.

**Quick Docker commands:**
- `docker-compose up -d` - Start container
- `docker-compose logs -f` - View logs
- `docker-compose down` - Stop container
- API docs: http://localhost:8000/docs

## 🛠️ Development

```bash
# Activate development environment
./activate.sh

# Run tests
python test_mvp.py
python test_docker_config.py

# Try examples
python examples/basic_usage.py
```

## 📋 Bot Commands

- `/start` - Get your API key and setup instructions
- `/revoke` - Generate a new API key
- `/status` - Check your connection status

## 🔧 API Endpoints

- `POST /api/notify` - Send notification
- `GET /api/validate` - Validate API key
- `POST /api/heartbeat` - Keep-alive
- `GET /docs` - Interactive API documentation

## 📁 Project Structure

```
ExperimentBot/
├── bot/                    # Telegram bot
├── server/                 # API server
├── client/                 # Python client library
├── examples/              # Usage examples
├── Dockerfile             # Container setup
├── docker-compose.yml     # Docker orchestration
└── start_*.py            # Service launchers
```

## 🔒 Security

- Unique API keys per user
- Token-based authentication
- Rate limiting and validation
- Secure key generation and rotation

This is an MVP implementation. See [CLAUDE.md](CLAUDE.md) for the full development roadmap and advanced features.
