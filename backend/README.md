# Cortex Backend

MLX-powered AI platform backend with LLM support, tools, and agents.

## Prerequisites

- **Apple Silicon Mac** (M1, M2, M3, M4, or M5)
- **macOS 13.0+**
- **Python 3.9+**

## Quick Start

### 1. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

> **Note:** First installation takes 2-3 minutes. MLX packages are optimized for Apple Silicon.

### 3. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` to customize settings (optional - defaults work out of the box).

### 4. Run the Server

```bash
# Using the run script (recommended)
python run.py

# Or use uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Server will start on http://localhost:8000

## Testing

### Manual API Testing

**1. Health Check:**
```bash
curl http://localhost:8000/api/health
```

**2. List Available Models:**
```bash
curl http://localhost:8000/api/models | python3 -m json.tool
```

**3. Chat Completion:**
```bash
curl -X POST http://localhost:8000/api/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Hello!"}],
    "max_tokens": 100,
    "temperature": 0.7
  }'
```

### Using the Test Script

A Python test script is provided for easy testing:

```bash
# Create test script
cat > test_api.py << 'EOF'
import requests
import json

response = requests.post(
    "http://localhost:8000/api/chat/completions",
    json={
        "messages": [{"role": "user", "content": "Hello! Say hi back."}],
        "max_tokens": 50,
        "temperature": 0.7
    }
)

print(f"Status: {response.status_code}")
print(json.dumps(response.json(), indent=2))
EOF

# Run test
python test_api.py
```

### Running Unit Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_chat.py -v
```

## API Endpoints

### Health & Info
- `GET /` - API information
- `GET /api/health` - Health check endpoint

### Models
- `GET /api/models` - List available models
- `POST /api/models/{model_id}/load` - Load a specific model
- `POST /api/models/{model_id}/unload` - Unload a model

### Chat Completions
- `POST /api/chat/completions` - Create a chat completion (synchronous)
- `POST /api/chat/completions/stream` - Create a streaming chat completion (SSE)
- `WS /api/chat/ws` - WebSocket endpoint for real-time chat

### API Documentation
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json

## Chat API Examples

### Basic Chat Completion

```python
import requests

response = requests.post(
    "http://localhost:8000/api/chat/completions",
    json={
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What is MLX?"}
        ],
        "temperature": 0.7,
        "max_tokens": 500
    }
)

print(response.json()["message"]["content"])
```

### Streaming Chat Completion

```python
import requests

response = requests.post(
    "http://localhost:8000/api/chat/completions/stream",
    json={
        "messages": [{"role": "user", "content": "Count to 10"}],
        "temperature": 0.7
    },
    stream=True
)

for line in response.iter_lines():
    if line:
        print(line.decode('utf-8'))
```

### WebSocket Chat

```python
import asyncio
import websockets
import json

async def chat():
    uri = "ws://localhost:8000/api/chat/ws"
    async with websockets.connect(uri) as websocket:
        # Send chat message
        await websocket.send(json.dumps({
            "type": "chat",
            "messages": [{"role": "user", "content": "Hello!"}],
            "temperature": 0.7
        }))

        # Receive responses
        while True:
            response = await websocket.recv()
            data = json.loads(response)
            if data["type"] == "done":
                break
            print(data)

asyncio.run(chat())
```

## Architecture

```
backend/
├── app/
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration management
│   ├── api/
│   │   ├── routes/          # REST API endpoints
│   │   │   ├── chat.py      # Chat completions
│   │   │   ├── models.py    # Model management
│   │   │   └── health.py    # Health checks
│   │   └── websocket/       # WebSocket endpoints
│   │       └── chat.py      # Real-time chat
│   ├── core/
│   │   ├── base_model.py    # Abstract model interface
│   │   └── llm_service.py   # MLX-LM implementation
│   ├── tools/               # Tool implementations
│   ├── agents/              # Agent implementations
│   └── schemas/             # Pydantic schemas
│       ├── chat.py
│       └── tools.py
├── requirements.txt
├── run.py
└── .env.example
```

## Available Models

The backend supports MLX-compatible models from Hugging Face:

| Model | Size | Speed | Memory | Best For |
|-------|------|-------|--------|----------|
| `mlx-community/Llama-3.2-3B-Instruct-4bit` | 1.7GB | ⚡⚡⚡ | 4GB | Default, Fast responses |
| `mlx-community/Meta-Llama-3.1-8B-Instruct-4bit` | 4.5GB | ⚡⚡ | 8GB | Balanced |
| `mlx-community/Qwen2.5-7B-Instruct-4bit` | 4.2GB | ⚡⚡ | 8GB | Instruction following |
| `mlx-community/Llama-3.3-70B-Instruct-4bit` | 39GB | ⚡ | 48GB | Best quality, M3 Max+ |

**Performance Notes:**
- First model download: 1-5 minutes (one-time)
- Model loading from cache: 1-3 seconds
- Inference: Real-time on Apple Silicon GPU

## Configuration

Environment variables in `.env`:

```bash
# Server
HOST=0.0.0.0
PORT=8000
DEBUG=True
ENVIRONMENT=development

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001

# Model Settings
DEFAULT_MODEL=mlx-community/Llama-3.2-3B-Instruct-4bit
MODEL_CACHE_DIR=~/.cache/mlx-models

# Generation Defaults
DEFAULT_MAX_TOKENS=2048
DEFAULT_TEMPERATURE=0.7
DEFAULT_TOP_P=0.9

# Tools & Agents
ENABLE_WEB_SEARCH=True
ENABLE_CODE_EXECUTION=True
ENABLE_FILE_OPERATIONS=False
ENABLE_AGENTS=True
```

## Development

### Code Quality

```bash
# Format code
black app/

# Lint code
ruff check app/

# Fix linting issues
ruff check app/ --fix
```

### Project Structure

- `app/core/` - Core abstractions (models, services)
- `app/api/routes/` - REST API endpoints
- `app/api/websocket/` - WebSocket handlers
- `app/schemas/` - Pydantic data models
- `app/tools/` - Tool implementations
- `app/agents/` - Agent implementations

## Features

### ✅ Implemented
- MLX-LM integration with Apple Silicon optimization
- Chat completions (synchronous & streaming)
- WebSocket real-time chat
- Multiple model support
- Model loading/unloading
- Temperature and top_p sampling
- Extensible model interface
- CORS support
- API documentation (Swagger/ReDoc)

### 🔄 In Progress
- Tool execution engine
- Function calling
- Agent system

### 📋 Planned
- Conversation history persistence
- RAG (Retrieval Augmented Generation)
- Vision models support
- Audio models support
- Multi-user authentication
- Rate limiting

## Troubleshooting

### Model Loading Issues

**Problem:** Model fails to download
```bash
# Solution: Check internet connection and disk space
df -h  # Check disk space
# Need ~10GB free for larger models
```

**Problem:** Model loading is slow
```bash
# Solution: Model is downloading for the first time
# Subsequent loads use cache and are much faster
# Check cache: ls -lh ~/.cache/mlx-models/
```

### Memory Issues

**Problem:** Out of memory errors
```bash
# Solutions:
# 1. Use smaller models (3B instead of 70B)
# 2. Unload unused models via API
# 3. Close other applications
# 4. For M1/M2 8GB: stick to 3B-7B models
```

**Example - Unload model:**
```bash
curl -X POST http://localhost:8000/api/models/mlx-community__Llama-3.2-3B-Instruct-4bit/unload
```

### Performance Issues

**Problem:** Slow inference
```bash
# Check if MLX is using GPU:
# Should see "Metal" device in logs
# Ensure latest macOS for M5 Neural Accelerator support

# Monitor GPU usage:
sudo powermetrics --samplers gpu_power -i1000 -n1
```

**Problem:** Server not starting
```bash
# Check if port 8000 is in use:
lsof -i :8000

# Kill process using port:
kill -9 <PID>

# Or use different port:
uvicorn app.main:app --port 8001
```

### Common Errors

**Error:** `generate_step() got an unexpected keyword argument 'temperature'`
- **Fixed in latest version** - Now uses `make_sampler()` for temperature/top_p

**Error:** `No module named 'mlx'`
```bash
# Solution: Activate virtual environment
source venv/bin/activate
pip install -r requirements.txt
```

**Error:** `CORS policy` in browser
```bash
# Solution: Add your frontend URL to ALLOWED_ORIGINS in .env
ALLOWED_ORIGINS=http://localhost:3000
```

## Technical Details

### MLX-LM Sampling

The backend uses MLX-LM's `make_sampler()` for temperature and top_p control:

```python
from mlx_lm import generate
from mlx_lm.sample_utils import make_sampler

sampler = make_sampler(temp=0.7, top_p=0.9)
response = generate(model, tokenizer, prompt, sampler=sampler)
```

### Async Model Loading

Models are loaded asynchronously to prevent blocking:

```python
# Models load in thread pool
loop = asyncio.get_event_loop()
model, tokenizer = await loop.run_in_executor(None, load, model_id)
```

### Model Registry

Loaded models are cached in memory:
- Automatic loading on first request
- Models persist across requests
- Manual unload via API
- Auto-cleanup on server shutdown

## Performance Benchmarks

Tested on M3 Pro (18GB RAM):

| Model | Loading | First Token | Throughput |
|-------|---------|-------------|------------|
| Llama 3.2 3B | 1.2s | 150ms | ~80 tok/s |
| Llama 3.1 8B | 2.1s | 250ms | ~50 tok/s |
| Qwen 2.5 7B | 1.9s | 230ms | ~55 tok/s |

*Results vary based on hardware and prompt length*

## Contributing

When adding new features:
1. Follow existing code structure
2. Add type hints
3. Update this README
4. Write tests
5. Run `black` and `ruff` before committing

## Support

- Issues: https://github.com/your-repo/issues
- MLX Documentation: https://ml-explore.github.io/mlx/
- MLX-LM: https://github.com/ml-explore/mlx-lm

## License

MIT
