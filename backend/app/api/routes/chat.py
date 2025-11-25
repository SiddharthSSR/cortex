"""Chat completion endpoints."""

import logging
import time
import uuid

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse

from app.config import get_settings
from app.schemas.chat import ChatRequest, ChatResponse, StreamChunk, Message, MessageRole
from app.core.llm_service import LLMModel
from app.agents import ReActAgent
from app.tools import get_tool_registry
from app.tools.code_generator import CodeGeneratorTool

router = APIRouter()
logger = logging.getLogger(__name__)


async def get_or_load_model(model_id: str, model_registry: dict) -> LLMModel:
    """Get model from registry or load it.

    Args:
        model_id: Model identifier
        model_registry: Registry of loaded models

    Returns:
        Loaded LLM model

    Raises:
        HTTPException: If model loading fails
    """
    if model_id not in model_registry:
        try:
            logger.info(f"Loading model: {model_id}")
            model = LLMModel(model_id)
            await model.load()
            model_registry[model_id] = model
        except Exception as e:
            logger.error(f"Failed to load model {model_id}: {e}")
            raise HTTPException(
                status_code=500, detail=f"Failed to load model: {str(e)}"
            )

    return model_registry[model_id]


@router.post("/chat/completions", response_model=ChatResponse)
async def chat_completion(request_data: ChatRequest, request: Request):
    """Create a chat completion (non-streaming).

    Args:
        request_data: Chat request data
        request: FastAPI request object

    Returns:
        Chat completion response
    """
    settings = get_settings()
    model_registry = request.app.state.model_registry

    # Get model ID
    model_id = request_data.model or settings.default_model

    # Get or load model
    try:
        model = await get_or_load_model(model_id, model_registry)
    except HTTPException:
        raise

    # Create response
    response_id = f"chatcmpl-{uuid.uuid4().hex[:8]}"
    created_at = int(time.time())

    # Generate response
    try:
        start_time = time.time()

        # Check if agent mode is enabled
        if request_data.enable_agent:
            # Use agent for response
            tool_registry = get_tool_registry()

            # Ensure code generator tool has LLM access
            code_gen_tool = tool_registry.get_tool("code_generator")
            if isinstance(code_gen_tool, CodeGeneratorTool):
                code_gen_tool.set_llm(model)

            # Create agent
            agent = ReActAgent(
                llm=model,
                tool_registry=tool_registry,
                max_iterations=10,
                verbose=True,
            )

            # Get the user's latest message
            user_message = request_data.messages[-1].content if request_data.messages else ""

            # Execute agent
            agent_result = await agent.execute(user_message)

            # Convert agent steps to response format
            from app.schemas.chat import AgentStep
            agent_steps = []
            for step in agent_result.steps:
                agent_steps.append(
                    AgentStep(
                        step_number=step.step_number,
                        thought=step.thought,
                        action=step.action,
                        action_input=step.action_input,
                        observation=step.observation,
                        status=step.status.value,
                    )
                )

            # Create response message
            response_message = Message(
                role=MessageRole.ASSISTANT,
                content=agent_result.final_answer or "I couldn't find an answer.",
            )

            return ChatResponse(
                id=response_id,
                model=model_id,
                created=created_at,
                message=response_message,
                usage={
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "total_tokens": 0,
                },
                finish_reason="stop",
                agent_steps=agent_steps,
            )

        else:
            # Regular LLM generation
            response_message = await model.generate(
                messages=request_data.messages,
                tools=request_data.tools,
                temperature=request_data.temperature,
                max_tokens=request_data.max_tokens,
                top_p=request_data.top_p,
            )

            generation_time = time.time() - start_time

            return ChatResponse(
                id=response_id,
                model=model_id,
                created=created_at,
                message=response_message,
                usage={
                    "prompt_tokens": 0,  # MLX-LM doesn't provide token counts
                    "completion_tokens": 0,
                    "total_tokens": 0,
                },
                finish_reason="stop",
            )

    except Exception as e:
        logger.error(f"Chat completion failed: {e}")
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")


@router.post("/chat/completions/stream")
async def chat_completion_stream(request_data: ChatRequest, request: Request):
    """Create a streaming chat completion.

    Args:
        request_data: Chat request data
        request: FastAPI request object

    Returns:
        Streaming response
    """
    settings = get_settings()
    model_registry = request.app.state.model_registry

    # Get model ID
    model_id = request_data.model or settings.default_model

    # Get or load model
    try:
        model = await get_or_load_model(model_id, model_registry)
    except HTTPException:
        raise

    async def stream_generator():
        """Generate streaming response."""
        try:
            response_id = f"chatcmpl-{uuid.uuid4().hex[:8]}"
            created_at = int(time.time())

            async for chunk in model.stream_generate(
                messages=request_data.messages,
                tools=request_data.tools,
                temperature=request_data.temperature,
                max_tokens=request_data.max_tokens,
                top_p=request_data.top_p,
            ):
                if chunk.get("type") == "error":
                    # Send error chunk
                    yield f"data: {{'error': '{chunk.get('error')}'}}\n\n"
                    break

                elif chunk.get("type") == "content":
                    # Send content delta
                    stream_chunk = StreamChunk(
                        id=response_id,
                        model=model_id,
                        created=created_at,
                        delta=chunk.get("delta", {}),
                        finish_reason=None,
                    )
                    yield f"data: {stream_chunk.model_dump_json()}\n\n"

                elif chunk.get("type") == "tool_calls":
                    # Send tool calls
                    stream_chunk = StreamChunk(
                        id=response_id,
                        model=model_id,
                        created=created_at,
                        delta={"tool_calls": chunk.get("tool_calls")},
                        finish_reason=None,
                    )
                    yield f"data: {stream_chunk.model_dump_json()}\n\n"

            # Send final chunk
            final_chunk = StreamChunk(
                id=response_id,
                model=model_id,
                created=created_at,
                delta={},
                finish_reason="stop",
            )
            yield f"data: {final_chunk.model_dump_json()}\n\n"
            yield "data: [DONE]\n\n"

        except Exception as e:
            logger.error(f"Streaming failed: {e}")
            yield f"data: {{'error': '{str(e)}'}}\n\n"

    return StreamingResponse(
        stream_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
