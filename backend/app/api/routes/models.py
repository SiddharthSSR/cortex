"""Model management endpoints."""

import logging
from typing import List

from fastapi import APIRouter, HTTPException, Request

from app.config import get_settings
from app.schemas.chat import ModelInfo, ModelsListResponse
from app.core.llm_service import LLMModel

router = APIRouter()
logger = logging.getLogger(__name__)

# Predefined popular models
POPULAR_MODELS = [
    {
        "id": "mlx-community/Llama-3.2-3B-Instruct-4bit",
        "name": "Llama 3.2 3B Instruct (4-bit)",
        "description": "Fast and efficient 3B parameter model",
        "capabilities": ["chat", "function-calling"],
    },
    {
        "id": "mlx-community/Llama-3.3-70B-Instruct-4bit",
        "name": "Llama 3.3 70B Instruct (4-bit)",
        "description": "Powerful 70B parameter model",
        "capabilities": ["chat", "function-calling", "reasoning"],
    },
    {
        "id": "mlx-community/Qwen2.5-7B-Instruct-4bit",
        "name": "Qwen 2.5 7B Instruct (4-bit)",
        "description": "Qwen 2.5 7B optimized for instructions",
        "capabilities": ["chat", "function-calling"],
    },
    {
        "id": "mlx-community/Meta-Llama-3.1-8B-Instruct-4bit",
        "name": "Llama 3.1 8B Instruct (4-bit)",
        "description": "Meta's Llama 3.1 8B model",
        "capabilities": ["chat", "function-calling"],
    },
]


@router.get("/models", response_model=ModelsListResponse)
async def list_models(request: Request):
    """List available models."""
    settings = get_settings()
    model_registry = request.app.state.model_registry

    models = []
    for model_info in POPULAR_MODELS:
        is_loaded = model_info["id"] in model_registry

        models.append(
            ModelInfo(
                id=model_info["id"],
                name=model_info["name"],
                type="llm",
                description=model_info.get("description"),
                capabilities=model_info.get("capabilities", []),
                loaded=is_loaded,
            )
        )

    return ModelsListResponse(models=models)


@router.post("/models/{model_id}/load")
async def load_model(model_id: str, request: Request):
    """Load a specific model."""
    try:
        # Decode model_id if it contains path separators
        model_path = model_id.replace("__", "/")

        model_registry = request.app.state.model_registry

        # Check if already loaded
        if model_path in model_registry:
            return {"status": "already_loaded", "model_id": model_path}

        # Load the model
        logger.info(f"Loading model: {model_path}")
        model = LLMModel(model_path)
        await model.load()

        # Add to registry
        model_registry[model_path] = model

        return {"status": "loaded", "model_id": model_path}

    except Exception as e:
        logger.error(f"Failed to load model {model_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to load model: {str(e)}")


@router.post("/models/{model_id}/unload")
async def unload_model(model_id: str, request: Request):
    """Unload a specific model."""
    try:
        model_path = model_id.replace("__", "/")
        model_registry = request.app.state.model_registry

        if model_path not in model_registry:
            raise HTTPException(status_code=404, detail="Model not loaded")

        # Unload the model
        model = model_registry[model_path]
        await model.unload()

        # Remove from registry
        del model_registry[model_path]

        return {"status": "unloaded", "model_id": model_path}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to unload model {model_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to unload model: {str(e)}")
