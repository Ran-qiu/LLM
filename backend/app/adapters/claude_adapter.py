from typing import List, Optional, AsyncIterator
from anthropic import AsyncAnthropic

from app.adapters.base_adapter import (
    BaseLLMAdapter,
    ChatMessage,
    ChatCompletionResponse
)
from app.core.logger import get_logger

logger = get_logger("claude_adapter")


class ClaudeAdapter(BaseLLMAdapter):
    """Adapter for Anthropic Claude API"""

    # Pricing per 1M tokens (as of 2024)
    PRICING = {
        "claude-3-opus": {"input": 15.0, "output": 75.0},
        "claude-3-sonnet": {"input": 3.0, "output": 15.0},
        "claude-3-haiku": {"input": 0.25, "output": 1.25},
        "claude-3-5-sonnet": {"input": 3.0, "output": 15.0},
    }

    def __init__(self, api_key: str, **kwargs):
        """
        Initialize Claude adapter.

        Args:
            api_key: Anthropic API key
            **kwargs: Additional configuration
        """
        super().__init__(api_key, **kwargs)
        self.client = AsyncAnthropic(api_key=api_key)
        logger.info("Claude adapter initialized")

    def _convert_messages(self, messages: List[ChatMessage]) -> tuple:
        """
        Convert messages to Claude format.

        Claude requires system message to be separate.
        """
        system_message = None
        chat_messages = []

        for msg in messages:
            if msg.role == "system":
                system_message = msg.content
            else:
                chat_messages.append({
                    "role": msg.role,
                    "content": msg.content
                })

        return system_message, chat_messages

    async def chat(
        self,
        messages: List[ChatMessage],
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> ChatCompletionResponse:
        """Send chat completion request to Claude."""
        try:
            system_message, chat_messages = self._convert_messages(messages)

            # Claude requires max_tokens
            if max_tokens is None:
                max_tokens = 4096

            params = {
                "model": model,
                "messages": chat_messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                **kwargs
            }

            if system_message:
                params["system"] = system_message

            response = await self.client.messages.create(**params)

            content = response.content[0].text
            usage = {
                "prompt_tokens": response.usage.input_tokens,
                "completion_tokens": response.usage.output_tokens,
                "total_tokens": response.usage.input_tokens + response.usage.output_tokens,
            }

            # Calculate cost
            cost = self._calculate_cost(
                model,
                usage["prompt_tokens"],
                usage["completion_tokens"]
            )

            logger.info(
                f"Claude chat completed: model={model}, "
                f"tokens={usage['total_tokens']}"
            )

            return ChatCompletionResponse(
                content=content,
                model=model,
                usage=usage,
                finish_reason=response.stop_reason,
                metadata={"cost": cost}
            )

        except Exception as e:
            logger.error(f"Claude chat error: {str(e)}")
            raise

    async def stream_chat(
        self,
        messages: List[ChatMessage],
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """Send streaming chat completion request to Claude."""
        try:
            system_message, chat_messages = self._convert_messages(messages)

            if max_tokens is None:
                max_tokens = 4096

            params = {
                "model": model,
                "messages": chat_messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": True,
                **kwargs
            }

            if system_message:
                params["system"] = system_message

            logger.info(f"Claude stream chat started: model={model}")

            async with self.client.messages.stream(**params) as stream:
                async for text in stream.text_stream:
                    yield text

        except Exception as e:
            logger.error(f"Claude stream chat error: {str(e)}")
            raise

    async def get_models(self) -> List[str]:
        """Get list of available Claude models."""
        # Anthropic doesn't have a models list endpoint
        # Return known models
        models = [
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307",
            "claude-3-5-sonnet-20241022",
        ]
        logger.info(f"Retrieved {len(models)} Claude models")
        return models

    def validate_config(self) -> bool:
        """Validate Claude adapter configuration."""
        if not self.api_key:
            raise ValueError("Anthropic API key is required")
        return True

    def _calculate_cost(
        self,
        model: str,
        prompt_tokens: int,
        completion_tokens: int
    ) -> float:
        """Calculate estimated cost for Claude request."""
        # Find the base model name
        base_model = None
        for key in self.PRICING.keys():
            if key in model:
                base_model = key
                break

        if not base_model or base_model not in self.PRICING:
            return 0.0

        pricing = self.PRICING[base_model]
        input_cost = (prompt_tokens / 1_000_000) * pricing["input"]
        output_cost = (completion_tokens / 1_000_000) * pricing["output"]

        return input_cost + output_cost
