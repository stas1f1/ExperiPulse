# Telegram Experiment Notification Bot - Development Instructions

## Project Overview

Build a Python library and Telegram bot system for sending notifications from experiments and long-running processes. The system should provide automatic key generation, process tracking, and rich notification capabilities.

## System Architecture Overview

Your system will consist of three main components:

### 1. **Telegram Bot Service**
- Handles message routing and user authentication
- Manages key generation and validation
- Maintains user-to-chat mappings

### 2. **Python Client Library**
- Provides simple API for notifications
- Includes process wrapper functionality
- Handles automatic metadata collection

### 3. **Backend API Server**
- Bridges client library and Telegram bot
- Manages authentication tokens
- Queues and rate-limits messages

### 3. **Database**
- Stores user mappings

## Detailed Development Plan

### **Phase 1: Foundation**

#### 1.1 Telegram Bot Setup
```python
# Core bot functionality needed:
- /start command → generate unique key
- /revoke command → invalidate current key
- /status command → check connection status
- Message formatting and routing
```

#### 1.2 Backend API Design
```python
# API Endpoints:
POST /api/register    # Register new user, return key
POST /api/notify      # Send notification
GET  /api/validate    # Validate key is active
POST /api/heartbeat   # Keep-alive for long processes
```

#### 1.3 Database Schema
```sql
users:
  - user_id (telegram)
  - api_key (unique)
  - chat_id
  - created_at
  - last_active

notifications:
  - id
  - user_id
  - message
  - metadata (json)
  - timestamp
  - status

processes:
  - id
  - user_id
  - process_uuid
  - name
  - status
  - started_at
  - ended_at
  - metadata
```

### **Phase 2: Core Library Development**

#### 2.1 Basic Client Structure
```python
class ExperimentBot:
    def __init__(self, api_key=None):
        # Auto-load from env if not provided
        self.api_key = api_key or os.getenv('EXPERIMENT_BOT_KEY')
    
    def notify(self, message, **kwargs):
        # Manual notification
    
    def wrap(self, func):
        # Decorator for functions
    
    @contextmanager
    def track(self, name):
        # Context manager for code blocks
```

#### 2.2 Automatic Metadata Collection
```python
# Gather:
- Python version
- Current script/module name
- Git commit hash (if available)
- Hostname/environment
- Virtual environment name
- Key libraries and versions (numpy, torch, etc.)
- Memory/CPU usage
```

#### 2.3 Process Wrapper Implementation
```python
class ProcessTracker:
    def __init__(self, bot, name=None):
        self.bot = bot
        self.name = name or self._infer_name()
        self.process_id = uuid.uuid4()
        
    def __enter__(self):
        # Send start notification
        # Start monitoring thread
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Send completion/error notification
        # Include runtime, memory peak, etc.
```

### **Phase 3: Advanced Features**

#### 3.1 Parallel Process Management
```python
# Tag system for distinguishing parallel runs:
- Automatic color coding
- Process tree visualization
- Parent-child relationship tracking
- Concurrent execution dashboard
```

#### 3.2 Rich Notifications
```python
# Message formatting:
- Markdown support
- Code blocks for errors
- Progress bars (text-based)
- Inline buttons for actions
- File attachments (logs, plots)
```

#### 3.3 Smart Error Handling
```python
# Error reporting features:
- Truncated stack traces
- Highlighting relevant lines
- Common error interpretations
- Retry mechanisms
- Error aggregation for loops
```

### **Phase 4: User Experience **

#### 4.1 Easy Setup Flow
```bash
# Installation and setup:
pip install experiment-bot

# First run:
>>> from experiment_bot import setup
>>> setup()
"Visit @YourExperimentBot and press /start"
"Your key: exp_k7x9m2n4..."
"Key saved to .env file!"
```

#### 4.2 Usage Patterns
```python
# Pattern 1: Quick notifications
from experiment_bot import bot
bot.notify("Training started")

# Pattern 2: Function decorator
@bot.track
def train_model(data):
    # Automatic start/end notifications
    return model

# Pattern 3: Context manager
with bot.track("Data preprocessing"):
    # Code block tracking
    process_data()

# Pattern 4: Progress tracking
for epoch in bot.track_progress(range(100)):
    # Periodic updates
    train_epoch()
```

### **Phase 5: Testing & Documentation**

#### 5.1 Testing Strategy
- Unit tests for library components
- Integration tests with mock Telegram API
- Load testing for concurrent processes
- Error injection testing
- Documentation examples testing

#### 5.2 Documentation
- Quick start guide
- API reference
- Common patterns cookbook
- Troubleshooting guide
- Migration guide for updates

## Technical Implementation Details

### Security Considerations
```python
# Key management:
- Use cryptographically secure random keys
- Implement key rotation
- Rate limiting per key
- IP allowlisting (optional)
- Message encryption in transit
```

### Performance Optimization
```python
# Efficiency measures:
- Async message sending
- Message batching for high frequency
- Local queuing with retry
- Minimal overhead monitoring
- Lazy imports for faster startup
```

### Configuration Structure
```yaml
# .experiment_bot.yml
api_key: ${EXPERIMENT_BOT_KEY}
settings:
  auto_git_info: true
  include_system_info: true
  error_verbosity: medium
  batch_messages: true
  heartbeat_interval: 60
notifications:
  on_start: true
  on_error: true
  on_success: true
  progress_interval: 10%
```

## Development Milestones

### Milestone 1: MVP
- [ ] Basic bot with /start command
- [ ] Simple API server
- [ ] Minimal Python client
- [ ] Manual notification sending

### Milestone 2: Core Features
- [ ] Process tracking
- [ ] Automatic metadata
- [ ] Error handling
- [ ] Parallel process support

### Milestone 3: Production Ready
- [ ] Full test coverage
- [ ] Documentation complete
- [ ] Performance optimized
- [ ] Published to PyPI

## Project Structure
```
telegram-experiment-bot/
├── bot/
│   ├── telegram_bot.py
│   ├── handlers.py
│   └── formatters.py
├── server/
│   ├── api.py
│   ├── auth.py
│   ├── database.py
│   └── queue.py
├── client/
│   ├── experiment_bot/
│   │   ├── __init__.py
│   │   ├── client.py
│   │   ├── tracker.py
│   │   ├── decorators.py
│   │   └── utils.py
│   └── setup.py
├── tests/
├── docs/
└── examples/
```

## Getting Started Checklist

1. **Set up Telegram bot**
   - Create bot with BotFather
   - Get bot token
   - Set up webhook or polling

2. **Initialize backend**
   - Choose framework (FastAPI recommended)
   - Set up PostgreSQL/SQLite
   - Deploy to cloud (Heroku/Railway/VPS)

3. **Create client library**
   - Start with minimal working version
   - Add features incrementally
   - Test with real experiments

4. **Iterate based on usage**
   - Gather feedback
   - Add requested features
   - Optimize common patterns

This structure provides a solid foundation that's both easy to use and highly extensible. Start with the MVP and iterate based on your specific needs!