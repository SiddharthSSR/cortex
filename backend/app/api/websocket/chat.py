"""WebSocket chat endpoint for real-time streaming."""

import json
import logging
import time
import uuid
from typing import Dict, Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.websockets import WebSocketState

from app.config import get_settings
from app.schemas.chat import ChatRequest, Message, MessageRole
from app.core.llm_service import LLMModel

router = APIRouter()
logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manage WebSocket connections."""

    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        """Accept and store a WebSocket connection."""
        await websocket.accept()
        self.active_connections[client_id] = websocket
        logger.info(f"Client {client_id} connected")

    def disconnect(self, client_id: str):
        """Remove a WebSocket connection."""
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            logger.info(f"Client {client_id} disconnected")

    async def send_json(self, client_id: str, data: Dict[str, Any]):
        """Send JSON data to a specific client."""
        if client_id in self.active_connections:
            websocket = self.active_connections[client_id]
            if websocket.client_state == WebSocketState.CONNECTED:
                await websocket.send_json(data)


manager = ConnectionManager()


@router.websocket("/chat/ws")
async def websocket_chat(websocket: WebSocket):
    """WebSocket endpoint for streaming chat.

    Message format:
    {
        "type": "chat",
        "messages": [...],
        "model": "model_id",
        "temperature": 0.7,
        "max_tokens": 2048,
        "tools": [...],
        "enable_agent": false
    }
    """
    client_id = str(uuid.uuid4())
    settings = get_settings()

    await manager.connect(websocket, client_id)

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()

            message_type = data.get("type")

            if message_type == "chat":
                await handle_chat_message(websocket, client_id, data)
            elif message_type == "ping":
                await manager.send_json(client_id, {"type": "pong"})
            else:
                await manager.send_json(
                    client_id, {"type": "error", "error": f"Unknown message type: {message_type}"}
                )

    except WebSocketDisconnect:
        manager.disconnect(client_id)
    except Exception as e:
        logger.error(f"WebSocket error for client {client_id}: {e}")
        try:
            await manager.send_json(
                client_id, {"type": "error", "error": str(e)}
            )
        except:
            pass
        manager.disconnect(client_id)


async def handle_chat_message(websocket: WebSocket, client_id: str, data: Dict[str, Any]):
    """Handle a chat message from the client."""
    settings = get_settings()

    try:
        # Parse request data
        messages_data = data.get("messages", [])
        model_id = data.get("model", settings.default_model)
        temperature = data.get("temperature", settings.default_temperature)
        max_tokens = data.get("max_tokens", settings.default_max_tokens)
        top_p = data.get("top_p", settings.default_top_p)
        tools = data.get("tools")
        enable_agent = data.get("enable_agent", False)

        # Convert messages
        messages = []
        for msg in messages_data:
            messages.append(
                Message(
                    role=MessageRole(msg.get("role")),
                    content=msg.get("content", ""),
                    tool_calls=msg.get("tool_calls"),
                )
            )

        # Get model from app state (WebSocket doesn't have request.app directly)
        # We'll need to import it from main or use a global registry
        from app.main import model_registry

        # Get or load model
        if model_id not in model_registry:
            await manager.send_json(
                client_id, {"type": "status", "status": "loading_model"}
            )

            logger.info(f"Loading model: {model_id}")
            model = LLMModel(model_id)
            await model.load()
            model_registry[model_id] = model

            await manager.send_json(
                client_id, {"type": "status", "status": "model_loaded"}
            )

        model = model_registry[model_id]

        # Send generation started
        response_id = f"chatcmpl-{uuid.uuid4().hex[:8]}"
        await manager.send_json(
            client_id,
            {
                "type": "start",
                "id": response_id,
                "model": model_id,
            },
        )

        # Stream generation
        full_response = ""
        async for chunk in model.stream_generate(
            messages=messages,
            tools=tools,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
        ):
            if chunk.get("type") == "error":
                await manager.send_json(
                    client_id,
                    {
                        "type": "error",
                        "id": response_id,
                        "error": chunk.get("error"),
                    },
                )
                break

            elif chunk.get("type") == "content":
                delta = chunk.get("delta", {})
                full_response = chunk.get("accumulated", full_response)

                await manager.send_json(
                    client_id,
                    {
                        "type": "delta",
                        "id": response_id,
                        "delta": delta,
                        "accumulated": full_response,
                    },
                )

            elif chunk.get("type") == "tool_calls":
                await manager.send_json(
                    client_id,
                    {
                        "type": "tool_calls",
                        "id": response_id,
                        "tool_calls": chunk.get("tool_calls"),
                    },
                )

        # Send completion
        await manager.send_json(
            client_id,
            {
                "type": "done",
                "id": response_id,
                "finish_reason": "stop",
                "full_response": full_response,
            },
        )

    except Exception as e:
        logger.error(f"Error handling chat message: {e}")
        await manager.send_json(
            client_id,
            {"type": "error", "error": str(e)},
        )
