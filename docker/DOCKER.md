# ExperimentBot Docker Setup

Run ExperimentBot in a Docker container with both Telegram bot and API server.

## Quick Start

### 1. Get Telegram Bot Token
1. Message [@BotFather](https://t.me/botfather) on Telegram
2. Create new bot: `/newbot`
3. Copy your bot token

### 2. Using Docker Compose (Recommended)

```bash
# Copy environment template
cp .env.docker .env

# Edit .env and set your bot token
nano .env
# Set: TELEGRAM_BOT_TOKEN=your_actual_token_here

# Start the container
docker-compose up -d

# View logs
docker-compose logs -f
```

### 3. Using Docker Run

```bash
# Build the image
docker build -t experiment-bot .

# Run the container
docker run -d \
  --name experiment-bot \
  -p 8000:8000 \
  -e TELEGRAM_BOT_TOKEN=your_bot_token_here \
  -v experiment_bot_data:/app/data \
  experiment-bot
```

## Container Features

✅ **Automatic Startup** - Both bot and API server start together
✅ **Persistent Data** - Database stored in Docker volume
✅ **Health Checks** - Container monitors service health
✅ **Graceful Shutdown** - Proper cleanup on container stop
✅ **Logging** - Combined logs from both services

## Accessing Services

- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/
- **Bot**: Message your Telegram bot directly

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `TELEGRAM_BOT_TOKEN` | *required* | Your Telegram bot token |
| `API_HOST` | `0.0.0.0` | API server host |
| `API_PORT` | `8000` | API server port |
| `DATABASE_PATH` | `/app/data/experiment_bot.db` | Database file path |

## Container Commands

```bash
# View logs
docker-compose logs -f experiment-bot

# Stop container
docker-compose down

# Restart container
docker-compose restart

# Update container
docker-compose pull && docker-compose up -d

# Shell access
docker-compose exec experiment-bot bash
```

## Data Persistence

The container uses a Docker volume to persist:
- SQLite database
- User registrations
- Notification history

Data survives container restarts and updates.

## Production Deployment

### Using Docker Compose

```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  experiment-bot:
    image: experiment-bot:latest
    ports:
      - "8000:8000"
    environment:
      - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
    volumes:
      - /var/lib/experiment-bot:/app/data
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 512M
        reservations:
          memory: 256M
```

### Using a Reverse Proxy

```nginx
# nginx configuration
location /experiment-bot/ {
    proxy_pass http://localhost:8000/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

## Troubleshooting

### Container won't start
- Check bot token: `docker logs experiment-bot`
- Verify port availability: `netstat -tulpn | grep 8000`

### Bot not responding
- Check Telegram token validity
- Ensure container is healthy: `docker ps`

### API not accessible
- Check port mapping: `docker port experiment-bot`
- Test health endpoint: `curl http://localhost:8000/`

### Database issues
- Check volume permissions: `docker volume inspect experiment_bot_data`
- Restart container: `docker-compose restart`

## Development

```bash
# Build development image
docker build -t experiment-bot:dev .

# Run with code mounting
docker run -it \
  -p 8000:8000 \
  -e TELEGRAM_BOT_TOKEN=your_token \
  -v $(pwd):/app \
  experiment-bot:dev bash
```