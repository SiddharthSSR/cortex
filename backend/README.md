# Cortex Backend

MLX-powered AI platform backend with LLM support, tools, and agents.

## Prerequisites

- **Apple Silicon Mac** (M1, M2, M3, M4, or M5)
- **macOS 13.0+**
- **Python 3.10+**

## Setup

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

### 3. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` to configure your settings.

### 4. Run the Server

```bash
# Development mode with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or use the run script
python run.py
```

## API Endpoints

### Health Check
- `GET /api/health` - Health check endpoint

### Models
- `GET /api/models` - List available models
- `POST /api/models/{model_id}/load` - Load a specific model
- `POST /api/models/{model_id}/unload` - Unload a model

### Chat
- `POST /api/chat/completions` - Create a chat completion (non-streaming)
- `POST /api/chat/completions/stream` - Create a streaming chat completion
- `WS /api/chat/ws` - WebSocket endpoint for real-time chat

## API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

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
└── requirements.txt
```

## Available Models

The backend supports any MLX-compatible model from Hugging Face. Popular options:

- `mlx-community/Llama-3.2-3B-Instruct-4bit` (Default - Fast)
- `mlx-community/Llama-3.3-70B-Instruct-4bit` (Powerful)
- `mlx-community/Qwen2.5-7B-Instruct-4bit`
- `mlx-community/Meta-Llama-3.1-8B-Instruct-4bit`

## Development

### Code Formatting
```bash
black app/
ruff check app/
```

### Testing
```bash
pytest
```

## Features

### Current
- ✅ MLX-LM integration
- ✅ Chat completions (sync & streaming)
- ✅ WebSocket support
- ✅ Multiple model support
- ✅ Model loading/unloading
- ✅ Function calling foundation

### Coming Soon
- 🔄 Tool execution engine
- 🔄 Agent system
- 🔄 Conversation history
- 🔄 RAG support
- 🔄 Vision models
- 🔄 Audio models

## Troubleshooting

### Model Loading Issues
- Ensure you have enough disk space (~10GB for larger models)
- First model load will download from Hugging Face
- Models are cached in `~/.cache/mlx-models/`

### Memory Issues
- Use 4-bit quantized models for lower memory usage
- Unload unused models via `/api/models/{model_id}/unload`
- For M1/M2 with 8GB RAM, stick to 3B-7B models

### Performance
- MLX automatically uses the GPU
- Ensure no other heavy processes are running
- For M5 Macs: Update to latest macOS for Neural Accelerator support

## License

MIT
