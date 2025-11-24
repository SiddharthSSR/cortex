"""Main FastAPI application."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.api.routes import chat, models, health
from app.api.websocket import chat as ws_chat

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

# Global model registry
model_registry = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    settings = get_settings()
    logger.info(f"Starting Cortex API (Environment: {settings.environment})")

    # Startup: Pre-load default model if needed
    # from app.core.llm_service import LLMModel
    # default_model = LLMModel(settings.default_model)
    # await default_model.load()
    # model_registry[settings.default_model] = default_model

    yield

    # Shutdown: Cleanup
    logger.info("Shutting down Cortex API")
    for model_id, model in model_registry.items():
        try:
            await model.unload()
            logger.info(f"Unloaded model: {model_id}")
        except Exception as e:
            logger.error(f"Error unloading model {model_id}: {e}")


# Create FastAPI app
app = FastAPI(
    title="Cortex API",
    description="MLX-powered AI platform with LLM, tools, and agents",
    version="0.1.0",
    lifespan=lifespan,
)

# Configure CORS
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(models.router, prefix="/api", tags=["Models"])
app.include_router(chat.router, prefix="/api", tags=["Chat"])
app.include_router(ws_chat.router, prefix="/api", tags=["WebSocket"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "Cortex API",
        "version": "0.1.0",
        "status": "running",
        "docs": "/docs",
    }


# Make model registry accessible to routes
app.state.model_registry = model_registry
