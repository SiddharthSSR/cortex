"""LLM Service using MLX-LM framework."""

import asyncio
import json
import time
from typing import Any, AsyncIterator, Dict, List, Optional
import logging

from app.core.base_model import BaseModel
from app.schemas.chat import Message, MessageRole

logger = logging.getLogger(__name__)


class LLMModel(BaseModel):
    """LLM implementation using MLX-LM."""

    def __init__(self, model_id: str, **kwargs):
        """Initialize the LLM model.

        Args:
            model_id: Hugging Face model ID or local path
            **kwargs: Additional configuration (cache_dir, etc.)
        """
        super().__init__(model_id, **kwargs)
        self.model = None
        self.tokenizer = None
        self._default_max_tokens = kwargs.get("max_tokens", 2048)
        self._default_temperature = kwargs.get("temperature", 0.7)

    async def load(self) -> None:
        """Load the MLX model and tokenizer."""
        if self._loaded:
            logger.info(f"Model {self.model_id} already loaded")
            return

        try:
            logger.info(f"Loading model: {self.model_id}")
            # Import here to avoid loading MLX if not needed
            from mlx_lm import load

            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            self.model, self.tokenizer = await loop.run_in_executor(
                None, lambda: load(self.model_id)
            )

            self._loaded = True
            logger.info(f"Model {self.model_id} loaded successfully")

        except Exception as e:
            logger.error(f"Failed to load model {self.model_id}: {e}")
            raise

    async def unload(self) -> None:
        """Unload the model from memory."""
        self.model = None
        self.tokenizer = None
        self._loaded = False
        logger.info(f"Model {self.model_id} unloaded")

    def _format_messages(self, messages: List[Message]) -> str:
        """Format messages for the model using chat template.

        Args:
            messages: List of conversation messages

        Returns:
            Formatted prompt string
        """
        # Convert messages to dict format
        message_dicts = []
        for msg in messages:
            message_dicts.append({"role": msg.role.value, "content": msg.content})

        # Use tokenizer's chat template if available
        if hasattr(self.tokenizer, "apply_chat_template"):
            try:
                prompt = self.tokenizer.apply_chat_template(
                    message_dicts, tokenize=False, add_generation_prompt=True
                )
                return prompt
            except Exception as e:
                logger.warning(f"Failed to apply chat template: {e}, using fallback")

        # Fallback to simple formatting
        formatted = ""
        for msg in messages:
            if msg.role == MessageRole.SYSTEM:
                formatted += f"System: {msg.content}\n\n"
            elif msg.role == MessageRole.USER:
                formatted += f"User: {msg.content}\n\n"
            elif msg.role == MessageRole.ASSISTANT:
                formatted += f"Assistant: {msg.content}\n\n"

        formatted += "Assistant: "
        return formatted

    async def generate(
        self,
        messages: List[Message],
        tools: Optional[List[Dict[str, Any]]] = None,
        **kwargs,
    ) -> Message:
        """Generate a response synchronously.

        Args:
            messages: List of conversation messages
            tools: Optional list of available tools (for function calling)
            **kwargs: Generation parameters (temperature, max_tokens, etc.)

        Returns:
            Generated message
        """
        if not self._loaded:
            await self.load()

        # Format messages
        prompt = self._format_messages(messages)

        # Add tools to prompt if provided
        if tools:
            tools_str = self._format_tools_for_prompt(tools)
            prompt = f"{tools_str}\n\n{prompt}"

        # Get generation parameters
        max_tokens = kwargs.get("max_tokens", self._default_max_tokens)
        temperature = kwargs.get("temperature", self._default_temperature)
        top_p = kwargs.get("top_p", 0.9)

        try:
            # Import generate function and sampler
            from mlx_lm import generate
            from mlx_lm.sample_utils import make_sampler

            # Create sampler with temperature and top_p
            sampler = make_sampler(temp=temperature, top_p=top_p)

            # Run generation in thread pool
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: generate(
                    self.model,
                    self.tokenizer,
                    prompt=prompt,
                    max_tokens=max_tokens,
                    sampler=sampler,
                    verbose=False,
                ),
            )

            # Parse tool calls if present
            tool_calls = None
            if tools:
                tool_calls = self._parse_tool_calls(response)

            return Message(
                role=MessageRole.ASSISTANT,
                content=response.strip(),
                tool_calls=tool_calls,
            )

        except Exception as e:
            logger.error(f"Generation failed: {e}")
            raise

    async def stream_generate(
        self,
        messages: List[Message],
        tools: Optional[List[Dict[str, Any]]] = None,
        **kwargs,
    ) -> AsyncIterator[Dict[str, Any]]:
        """Generate a response with streaming.

        Args:
            messages: List of conversation messages
            tools: Optional list of available tools
            **kwargs: Generation parameters

        Yields:
            Streaming chunks with delta content
        """
        if not self._loaded:
            await self.load()

        # Format messages
        prompt = self._format_messages(messages)

        # Add tools to prompt if provided
        if tools:
            tools_str = self._format_tools_for_prompt(tools)
            prompt = f"{tools_str}\n\n{prompt}"

        # Get generation parameters
        max_tokens = kwargs.get("max_tokens", self._default_max_tokens)
        temperature = kwargs.get("temperature", self._default_temperature)
        top_p = kwargs.get("top_p", 0.9)

        try:
            # Import stream_generate function and sampler
            from mlx_lm import stream_generate
            from mlx_lm.sample_utils import make_sampler

            # Create sampler with temperature and top_p
            sampler = make_sampler(temp=temperature, top_p=top_p)

            # Create a queue for streaming
            queue = asyncio.Queue()

            def stream_worker():
                """Worker to handle streaming in thread."""
                try:
                    for chunk in stream_generate(
                        self.model,
                        self.tokenizer,
                        prompt=prompt,
                        max_tokens=max_tokens,
                        sampler=sampler,
                    ):
                        asyncio.run_coroutine_threadsafe(
                            queue.put(chunk), asyncio.get_event_loop()
                        )
                except Exception as e:
                    asyncio.run_coroutine_threadsafe(
                        queue.put({"error": str(e)}), asyncio.get_event_loop()
                    )
                finally:
                    asyncio.run_coroutine_threadsafe(
                        queue.put(None), asyncio.get_event_loop()
                    )

            # Start streaming in thread pool
            loop = asyncio.get_event_loop()
            loop.run_in_executor(None, stream_worker)

            # Yield chunks as they arrive
            full_response = ""
            while True:
                chunk = await queue.get()

                if chunk is None:
                    # Streaming complete
                    break

                if "error" in chunk:
                    yield {"type": "error", "error": chunk["error"]}
                    break

                # Extract text from chunk
                if hasattr(chunk, "text"):
                    text = chunk.text
                elif isinstance(chunk, dict) and "text" in chunk:
                    text = chunk["text"]
                else:
                    text = str(chunk)

                full_response += text

                yield {
                    "type": "content",
                    "delta": {"content": text},
                    "accumulated": full_response,
                }

            # Check for tool calls in final response
            if tools and full_response:
                tool_calls = self._parse_tool_calls(full_response)
                if tool_calls:
                    yield {"type": "tool_calls", "tool_calls": tool_calls}

        except Exception as e:
            logger.error(f"Streaming generation failed: {e}")
            yield {"type": "error", "error": str(e)}

    def _format_tools_for_prompt(self, tools: List[Dict[str, Any]]) -> str:
        """Format tools for inclusion in prompt.

        Args:
            tools: List of tool definitions

        Returns:
            Formatted tools string
        """
        tools_desc = "You have access to the following tools:\n\n"
        for tool in tools:
            func = tool.get("function", {})
            name = func.get("name", "")
            description = func.get("description", "")
            parameters = func.get("parameters", {})

            tools_desc += f"- {name}: {description}\n"
            tools_desc += f"  Parameters: {json.dumps(parameters, indent=2)}\n\n"

        tools_desc += "\nTo use a tool, respond with JSON in this format:\n"
        tools_desc += '{"tool": "tool_name", "parameters": {...}}\n'

        return tools_desc

    def _parse_tool_calls(self, response: str) -> Optional[List[Dict[str, Any]]]:
        """Parse tool calls from model response.

        Args:
            response: Model's text response

        Returns:
            List of tool calls if found, None otherwise
        """
        try:
            # Try to find JSON in response
            start = response.find("{")
            end = response.rfind("}") + 1

            if start != -1 and end > start:
                json_str = response[start:end]
                tool_call = json.loads(json_str)

                if "tool" in tool_call:
                    return [
                        {
                            "id": f"call_{int(time.time())}",
                            "type": "function",
                            "function": {
                                "name": tool_call["tool"],
                                "arguments": json.dumps(
                                    tool_call.get("parameters", {})
                                ),
                            },
                        }
                    ]
        except Exception as e:
            logger.debug(f"No tool calls found in response: {e}")

        return None

    @property
    def model_type(self) -> str:
        """Return the type of model."""
        return "llm"

    def get_capabilities(self) -> List[str]:
        """Return list of model capabilities."""
        return ["chat", "text-generation", "function-calling"]
