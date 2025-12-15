from typing import List, Optional, AsyncIterator
from openai import AsyncOpenAI

from app.adapters.base_adapter import (
    BaseLLMAdapter,
    ChatMessage,
    ChatCompletionResponse
)
from app.core.logger import get_logger

logger = get_logger("openai_adapter")


class OpenAIAdapter(BaseLLMAdapter):
    """Adapter for OpenAI API"""

    # Pricing per 1M tokens (as of 2024)
    PRICING = {
        "gpt-4": {"input": 30.0, "output": 60.0},
        "gpt-4-turbo": {"input": 10.0, "output": 30.0},
        "gpt-4o": {"input": 5.0, "output": 15.0},
        "gpt-4o-mini": {"input": 0.15, "output": 0.6},
        "gpt-3.5-turbo": {"input": 0.5, "output": 1.5},
    }

    def __init__(self, api_key: str, base_url: Optional[str] = None, **kwargs):
        """
        Initialize OpenAI adapter.

        Args:
            api_key: OpenAI API key
            base_url: Optional custom base URL (for Azure OpenAI, etc.)
            **kwargs: Additional configuration
        """
        super().__init__(api_key, **kwargs)
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url
        )
        logger.info("OpenAI adapter initialized")

    async def chat(
        self,
        messages: List[ChatMessage],
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> ChatCompletionResponse:
        """Send chat completion request to OpenAI."""
        try:
            formatted_messages = self._format_messages(messages)

            response = await self.client.chat.completions.create(
                model=model,
                messages=formatted_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )

            content = response.choices[0].message.content
            usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            } if response.usage else None

            # Calculate cost
            cost = None
            if usage:
                cost = self._calculate_cost(
                    model,
                    usage["prompt_tokens"],
                    usage["completion_tokens"]
                )

            logger.info(
                f"OpenAI chat completed: model={model}, "
                f"tokens={usage['total_tokens'] if usage else 'unknown'}"
            )

            return ChatCompletionResponse(
                content=content,
                model=model,
                usage=usage,
                finish_reason=response.choices[0].finish_reason,
                metadata={"cost": cost} if cost else None
            )

        except Exception as e:
            logger.error(f"OpenAI chat error: {str(e)}")
            raise

    async def stream_chat(
        self,
        messages: List[ChatMessage],
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """Send streaming chat completion request to OpenAI."""
        try:
            formatted_messages = self._format_messages(messages)

            stream = await self.client.chat.completions.create(
                model=model,
                messages=formatted_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
                **kwargs
            )

            logger.info(f"OpenAI stream chat started: model={model}")

            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            logger.error(f"OpenAI stream chat error: {str(e)}")
            raise

    async def get_models(self) -> List[str]:
        """Get list of available OpenAI models."""
        try:
            models = await self.client.models.list()
            model_ids = [model.id for model in models.data]
            logger.info(f"Retrieved {len(model_ids)} OpenAI models")
            return model_ids
        except Exception as e:
            logger.error(f"Failed to get OpenAI models: {str(e)}")
            raise

    def validate_config(self) -> bool:
        """Validate OpenAI adapter configuration."""
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
        return True

    def _calculate_cost(
        self,
        model: str,
        prompt_tokens: int,
        completion_tokens: int
    ) -> float:
        """Calculate estimated cost for OpenAI request."""
        # Find the base model name
        base_model = model
        for key in self.PRICING.keys():
            if model.startswith(key):
                base_model = key
                break

        if base_model not in self.PRICING:
            return 0.0

        pricing = self.PRICING[base_model]
        input_cost = (prompt_tokens / 1_000_000) * pricing["input"]
        output_cost = (completion_tokens / 1_000_000) * pricing["output"]

        return input_cost + output_cost
