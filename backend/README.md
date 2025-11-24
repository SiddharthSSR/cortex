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

## Tools System

The Cortex backend includes a powerful tools system that allows LLMs and agents to interact with external capabilities.

### Available Tools

#### 1. Calculator Tool
Mathematical expression evaluator using SymPy for safe, accurate calculations.

**Capabilities:**
- Basic arithmetic: `+, -, *, /, **` (power)
- Functions: `sqrt(), sin(), cos(), tan(), log(), exp()`
- Constants: `pi, e`
- Complex expressions: `2**8 + sqrt(16) * pi`

**Example:**
```bash
curl -X POST http://localhost:8000/api/tools/execute \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "calculator",
    "parameters": {"expression": "2**10 + sqrt(144)"}
  }'
```

**Response:**
```json
{
  "success": true,
  "result": "1036",
  "error": null
}
```

#### 2. Web Search Tool
Search the web using DuckDuckGo (no API key required).

**Capabilities:**
- Web search with customizable result count
- Returns title, URL, and snippet for each result
- No API key or authentication needed

**Example:**
```bash
curl -X POST http://localhost:8000/api/tools/execute \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "web_search",
    "parameters": {
      "query": "Python programming tutorial",
      "num_results": 3
    }
  }'
```

**Response:**
```json
{
  "success": true,
  "result": [
    {
      "title": "Python Tutorial - W3Schools",
      "url": "https://www.w3schools.com/python/",
      "snippet": "Learn Python programming with examples..."
    }
  ]
}
```

#### 3. Python REPL Tool
Execute Python code in a sandboxed environment.

**Capabilities:**
- Safe code execution with restricted built-ins
- Allowed modules: `math`, `json`, `datetime`, `random`, `itertools`, `collections`
- Captures stdout and stderr
- Timeout protection (10 seconds)

**Security:**
- No file I/O operations
- No network access
- No system commands
- No dangerous built-ins (eval, exec, import, etc.)

**Example:**
```bash
curl -X POST http://localhost:8000/api/tools/execute \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "python_repl",
    "parameters": {
      "code": "import math\nprint([x**2 for x in range(1, 6)])\nprint(f\"Pi = {math.pi:.2f}\")"
    }
  }'
```

**Response:**
```json
{
  "success": true,
  "result": "[1, 4, 9, 16, 25]\nPi = 3.14\n"
}
```

#### 4. Code Generator Tool
Generate code based on natural language descriptions using LLM.

**Capabilities:**
- Generate code in multiple languages (Python, JavaScript, Go, etc.)
- Produces production-ready code with:
  - Proper documentation and docstrings
  - Type hints and error handling
  - Detailed comments explaining logic
  - Example usage code
- Uses lower temperature (0.3) for more deterministic output
- Automatically extracts code from markdown blocks

**Supported Languages:**
- Python (default)
- JavaScript
- Go
- Java
- Rust
- Any language the LLM supports

**Example - Generate Factorial Function:**
```bash
curl -X POST http://localhost:8000/api/tools/execute \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "code_generator",
    "parameters": {
      "request": "Create a function to calculate the factorial of a number",
      "language": "python"
    }
  }'
```

**Response:**
```json
{
  "success": true,
  "result": "def calculate_factorial(n: int) -> int:\n    \"\"\"\n    Calculate the factorial of a given number.\n    \n    Args:\n        n (int): The number to calculate the factorial for.\n    \n    Returns:\n        int: The factorial of the given number.\n    \n    Raises:\n        ValueError: If the input number is negative.\n    \"\"\"\n    if n < 0:\n        raise ValueError(\"Input number cannot be negative.\")\n    \n    result = 1\n    for i in range(2, n + 1):\n        result *= i\n    \n    return result"
}
```

**Example - Generate Binary Search:**
```bash
curl -X POST http://localhost:8000/api/tools/execute \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "code_generator",
    "parameters": {
      "request": "Write a binary search algorithm",
      "language": "python"
    }
  }'
```

**Use Cases:**
- Generate boilerplate code quickly
- Create utility functions on demand
- Prototype algorithms
- Generate code snippets for learning
- **Agent workflows**: Agent can generate code, then execute it with Python REPL

**Agent Integration:**
The code generator is especially powerful when used by agents:
```python
# Agent workflow example:
# 1. Agent uses code_generator to create a Fibonacci function
# 2. Agent uses python_repl to execute the generated code
# 3. Agent returns the result

response = requests.post(
    "http://localhost:8000/api/agents/execute",
    json={
        "goal": "Generate a function to calculate Fibonacci numbers, then use it to find the 10th Fibonacci number",
        "max_iterations": 15
    }
)
```

### Tools API Endpoints

#### List All Tools
```bash
GET /api/tools
```

**Response:**
```json
{
  "tools": [
    {
      "name": "calculator",
      "description": "Evaluate mathematical expressions",
      "parameters": {
        "expression": {
          "name": "expression",
          "type": "string",
          "description": "Mathematical expression to evaluate",
          "required": true
        }
      },
      "enabled": true
    }
  ]
}
```

#### Execute a Tool
```bash
POST /api/tools/execute
```

**Request Body:**
```json
{
  "tool_name": "calculator",
  "parameters": {
    "expression": "sqrt(16) * 5"
  }
}
```

#### Enable/Disable Tools
```bash
POST /api/tools/{tool_name}/enable
POST /api/tools/{tool_name}/disable
```

#### Get OpenAI-Compatible Tool Definitions
```bash
GET /api/tools/definitions/openai
```

Returns tool definitions in OpenAI function calling format for LLM integration.

### Using Tools in Python

```python
import requests

# Execute calculator
response = requests.post(
    "http://localhost:8000/api/tools/execute",
    json={
        "tool_name": "calculator",
        "parameters": {"expression": "2**16"}
    }
)
result = response.json()
print(f"Result: {result['result']}")  # Output: 65536

# Web search
response = requests.post(
    "http://localhost:8000/api/tools/execute",
    json={
        "tool_name": "web_search",
        "parameters": {
            "query": "MLX framework Apple",
            "num_results": 5
        }
    }
)
search_results = response.json()['result']
for item in search_results:
    print(f"{item['title']}: {item['url']}")

# Execute Python code
response = requests.post(
    "http://localhost:8000/api/tools/execute",
    json={
        "tool_name": "python_repl",
        "parameters": {
            "code": """
import math
fibonacci = [0, 1]
for i in range(8):
    fibonacci.append(fibonacci[-1] + fibonacci[-2])
print(f"Fibonacci sequence: {fibonacci}")
"""
        }
    }
)
print(response.json()['result'])

# Generate code
response = requests.post(
    "http://localhost:8000/api/tools/execute",
    json={
        "tool_name": "code_generator",
        "parameters": {
            "request": "Create a function to check if a string is a palindrome",
            "language": "python"
        }
    }
)
generated_code = response.json()['result']
print("Generated Code:")
print(generated_code)
```

### Adding Custom Tools

To create a custom tool, extend the `BaseTool` class:

```python
# app/tools/my_custom_tool.py
from typing import Dict
from app.tools.base_tool import BaseTool, ToolParameter, ToolResult

class MyCustomTool(BaseTool):
    @property
    def name(self) -> str:
        return "my_custom_tool"

    @property
    def description(self) -> str:
        return "Description of what this tool does"

    @property
    def parameters(self) -> Dict[str, ToolParameter]:
        return {
            "input_param": ToolParameter(
                name="input_param",
                type="string",
                description="Description of the parameter",
                required=True
            )
        }

    async def execute(self, input_param: str) -> ToolResult:
        try:
            # Your tool logic here
            result = f"Processed: {input_param}"
            return ToolResult(success=True, result=result)
        except Exception as e:
            return ToolResult(success=False, error=str(e))
```

Then register it in `app/tools/__init__.py`:

```python
from app.tools.my_custom_tool import MyCustomTool

def initialize_tools() -> ToolRegistry:
    registry = ToolRegistry()
    registry.register(CalculatorTool())
    registry.register(WebSearchTool())
    registry.register(PythonREPLTool())
    registry.register(MyCustomTool())  # Add your tool
    return registry
```

## Agent System

The Cortex backend includes an intelligent agent system that can autonomously solve complex tasks using available tools.

### What is ReAct?

**ReAct** stands for **Reasoning and Acting**. It's a framework where AI agents alternate between:
1. **Reasoning** (thinking about what to do)
2. **Acting** (using tools to accomplish tasks)

This creates a loop that continues until the agent reaches its goal.

### How ReAct Works

The ReAct agent follows this cycle:

```
1. THOUGHT  → Agent reasons about the current situation and decides what to do next
2. ACTION   → Agent selects a tool to use
3. INPUT    → Agent provides parameters for the tool
4. OBSERVE  → Agent receives the result from the tool
5. REPEAT   → Goes back to step 1 with new information
6. FINISH   → When goal is achieved, agent returns final answer
```

**Example Flow:**

```
Goal: "What is 2 to the power of 10?"

Step 1:
  Thought: I need to calculate 2^10. I should use the calculator tool.
  Action: calculator
  Action Input: {"expression": "2**10"}
  Observation: Success: 1024

Step 2:
  Thought: I have the answer. 2^10 equals 1024.
  Action: finish
  Action Input: {"answer": "1024"}

Result: ✅ 1024
```

### Why ReAct is Powerful

- **Self-correction**: If a tool fails, the agent can try a different approach
- **Multi-step reasoning**: Can break down complex problems into smaller steps
- **Tool composition**: Can use multiple tools in sequence to solve a problem
- **Transparency**: Every step is logged, making the reasoning process visible

### Agent API Endpoints

#### 1. Create a Plan

Generate a step-by-step plan for achieving a goal (without executing):

```bash
POST /api/agents/plan
```

**Request:**
```json
{
  "goal": "Find information about Python and calculate the sum of first 5 prime numbers"
}
```

**Response:**
```json
{
  "plan": "1. Use web_search to find information about Python\n2. Use python_repl to generate first 5 prime numbers\n3. Use calculator to sum them up\n4. Provide final answer",
  "goal": "Find information about Python and calculate the sum of first 5 prime numbers"
}
```

#### 2. Execute Agent

Run the agent to achieve a goal:

```bash
POST /api/agents/execute
```

**Request:**
```json
{
  "goal": "What is the factorial of 5?",
  "max_iterations": 10,
  "verbose": true
}
```

**Response:**
```json
{
  "success": true,
  "final_answer": "The factorial of 5 is 120",
  "steps": [
    {
      "step_number": 1,
      "thought": "I need to calculate 5! which is 5*4*3*2*1. I'll use the calculator.",
      "action": "calculator",
      "action_input": {"expression": "5*4*3*2*1"},
      "observation": "Success: 120",
      "status": "observing"
    },
    {
      "step_number": 2,
      "thought": "I have calculated that 5! = 120. This is the final answer.",
      "action": "finish",
      "action_input": {"answer": "The factorial of 5 is 120"},
      "observation": null,
      "status": "completed"
    }
  ],
  "metadata": {
    "iterations": 2,
    "goal": "What is the factorial of 5?"
  }
}
```

#### 3. Get Agent Info

Get information about available agents:

```bash
GET /api/agents/info
```

**Response:**
```json
{
  "agents": [
    {
      "type": "react",
      "name": "ReAct Agent",
      "description": "Agent that uses reasoning and acting to solve problems with tools",
      "capabilities": [
        "Multi-step reasoning",
        "Tool usage",
        "Self-correction",
        "Goal-oriented problem solving"
      ]
    }
  ]
}
```

### Agent Examples

#### Example 1: Simple Math Problem

```python
import requests

response = requests.post(
    "http://localhost:8000/api/agents/execute",
    json={
        "goal": "What is 2 to the power of 10?",
        "max_iterations": 5,
        "verbose": True
    }
)

result = response.json()
print(f"Success: {result['success']}")
print(f"Answer: {result['final_answer']}")
print(f"\nExecution trace:")
for step in result['steps']:
    print(f"\nStep {step['step_number']}:")
    print(f"  Thought: {step['thought']}")
    if step['action']:
        print(f"  Action: {step['action']}")
        print(f"  Input: {step['action_input']}")
    if step['observation']:
        print(f"  Observation: {step['observation']}")
```

**Output:**
```
Success: True
Answer: 1024

Execution trace:

Step 1:
  Thought: I need to calculate 2^10 using the calculator tool
  Action: calculator
  Input: {'expression': '2**10'}
  Observation: Success: 1024

Step 2:
  Thought: I have the answer, 2^10 = 1024
  Action: finish
  Input: {'answer': '1024'}
```

#### Example 2: Multi-Step Task

```python
response = requests.post(
    "http://localhost:8000/api/agents/execute",
    json={
        "goal": "Calculate the sum of squares from 1 to 5",
        "max_iterations": 10
    }
)

result = response.json()
print(f"Final Answer: {result['final_answer']}")
```

The agent will:
1. **Think**: Break down the problem (1² + 2² + 3² + 4² + 5²)
2. **Act**: Use calculator to compute "1**2 + 2**2 + 3**2 + 4**2 + 5**2"
3. **Observe**: Get result (55)
4. **Finish**: Return "The sum of squares from 1 to 5 is 55"

#### Example 3: Research + Computation

```python
response = requests.post(
    "http://localhost:8000/api/agents/execute",
    json={
        "goal": "Search for information about the Fibonacci sequence and then calculate the 10th Fibonacci number",
        "max_iterations": 10
    }
)
```

The agent will:
1. Use **web_search** to learn about Fibonacci
2. Use **python_repl** to write code calculating the 10th number
3. Return the result with explanation

### Agent Configuration

Configure agents via environment variables:

```bash
# .env
ENABLE_AGENTS=True
MAX_AGENT_ITERATIONS=10
DEFAULT_AGENT_VERBOSE=True
```

Or per-request:

```python
response = requests.post(
    "http://localhost:8000/api/agents/execute",
    json={
        "goal": "Your goal here",
        "model": "mlx-community/Llama-3.1-8B-Instruct-4bit",  # Optional
        "max_iterations": 15,  # Override default
        "verbose": True,       # Enable detailed logging
        "context": {           # Additional context
            "user_preference": "detailed explanations"
        }
    }
)
```

### Agent Use Cases

- **Mathematical Problem Solving**: Complex calculations requiring multiple steps
- **Research Tasks**: Search for information and synthesize answers
- **Data Processing**: Use Python to analyze and transform data
- **Multi-Tool Workflows**: Tasks requiring calculator + web search + code execution
- **Iterative Refinement**: Self-correcting when initial approaches fail

### Agent Best Practices

1. **Clear Goals**: Provide specific, well-defined goals
   - ✅ Good: "Calculate the average of the first 10 prime numbers"
   - ❌ Bad: "Do something with primes"

2. **Appropriate Iterations**: Set `max_iterations` based on task complexity
   - Simple math: 3-5 iterations
   - Multi-step tasks: 10-15 iterations
   - Complex research: 15-20 iterations

3. **Error Handling**: Agents will retry on failures, but check the execution trace

4. **Model Selection**: Larger models (8B+) perform better for complex reasoning

### ReAct Prompt Engineering

The ReAct agent uses a carefully engineered prompt that includes:

1. **Explicit Format Requirements**: Clear instructions on JSON formatting for tool calls
2. **Concrete Examples**: Examples for each tool showing exact parameter names and formats
3. **Common Mistakes**: Warnings about frequent errors (e.g., using "input" instead of "code")
4. **Multi-Step Workflows**: Complete examples showing how to chain tools together
5. **Tool Parameter Details**: Each tool shows parameter name, type, required/optional status

**Example from the prompt:**
```
Example 2 - python_repl tool requires "code" parameter (NOT "input"):
Thought: I need to execute Python code to create a list
Action: python_repl
Action Input: {"code": "print([x**2 for x in range(5)])"}
```

This explicit prompting significantly improves agent reliability and reduces formatting errors.

### Testing Agents

A complete test script is provided:

```bash
python test_agents.py
```

Or test manually:

```bash
# Test agent info
curl http://localhost:8000/api/agents/info | python3 -m json.tool

# Test planning
curl -X POST http://localhost:8000/api/agents/plan \
  -H "Content-Type: application/json" \
  -d '{"goal": "Calculate the sum of squares from 1 to 10"}' \
  | python3 -m json.tool

# Test execution
curl -X POST http://localhost:8000/api/agents/execute \
  -H "Content-Type: application/json" \
  -d '{
    "goal": "What is 2 to the power of 8?",
    "max_iterations": 5,
    "verbose": true
  }' | python3 -m json.tool
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
- **Tools System**:
  - Calculator (SymPy-based mathematical expressions)
  - Web Search (DuckDuckGo integration)
  - Python REPL (sandboxed code execution)
  - Code Generator (LLM-powered code generation in multiple languages)
  - Tool registry and management
  - OpenAI-compatible tool definitions
- **Agent System**:
  - ReAct (Reasoning + Acting) agent
  - Multi-step problem solving
  - Tool usage and composition
  - Planning and execution endpoints

### 📋 Planned
- Additional tools (file operations, HTTP client)
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
