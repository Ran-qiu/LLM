from typing import List, Optional, AsyncIterator
from openai import AsyncOpenAI

from app.adapters.base_adapter import (
    BaseLLMAdapter,
    ChatMessage,
    ChatCompletionResponse
)
from app.core.logger import get_logger

logger = get_logger("custom_adapter")


class CustomAdapter(BaseLLMAdapter):
    """
    Adapter for custom OpenAI-compatible API endpoints.

    Supports services like:
    - OneAPI
    - vLLM
    - FastChat
    - Text-generation-webui
    - Any other OpenAI-compatible API
    """

    def __init__(
        self,
        api_key: str,
        base_url: str,
        model_type: str = "openai-compatible",
        **kwargs
    ):
        """
        Initialize custom adapter.

        Args:
            api_key: API key for the custom endpoint
            base_url: Base URL of the custom API endpoint
            model_type: Type identifier for the custom model
            **kwargs: Additional configuration
        """
        super().__init__(api_key, **kwargs)
        self.base_url = base_url
        self.model_type = model_type

        # Use OpenAI client with custom base URL
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url
        )

        logger.info(f"Custom adapter initialized: {base_url} ({model_type})")

    async def chat(
        self,
        messages: List[ChatMessage],
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> ChatCompletionResponse:
        """Send chat completion request to custom endpoint."""
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

            # Try to get usage info if available
            usage = None
            if response.usage:
                usage = {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                }

            logger.info(
                f"Custom API chat completed: model={model}, "
                f"endpoint={self.base_url}, "
                f"tokens={usage['total_tokens'] if usage else 'unknown'}"
            )

            return ChatCompletionResponse(
                content=content,
                model=model,
                usage=usage,
                finish_reason=response.choices[0].finish_reason,
                metadata={
                    "base_url": self.base_url,
                    "model_type": self.model_type
                }
            )

        except Exception as e:
            logger.error(f"Custom API chat error: {str(e)}")
            raise

    async def stream_chat(
        self,
        messages: List[ChatMessage],
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """Send streaming chat completion request to custom endpoint."""
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

            logger.info(
                f"Custom API stream chat started: model={model}, "
                f"endpoint={self.base_url}"
            )

            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            logger.error(f"Custom API stream chat error: {str(e)}")
            raise

    async def get_models(self) -> List[str]:
        """Get list of available models from custom endpoint."""
        try:
            models = await self.client.models.list()
            model_ids = [model.id for model in models.data]
            logger.info(
                f"Retrieved {len(model_ids)} models from {self.base_url}"
            )
            return model_ids
        except Exception as e:
            logger.warning(
                f"Failed to get models from {self.base_url}: {str(e)}"
            )
            # Return empty list if endpoint doesn't support model listing
            return []

    def validate_config(self) -> bool:
        """Validate custom adapter configuration."""
        if not self.api_key:
            raise ValueError("API key is required for custom endpoint")
        if not self.base_url:
            raise ValueError("Base URL is required for custom endpoint")
        return True

    def _calculate_cost(
        self,
        model: str,
        prompt_tokens: int,
        completion_tokens: int
    ) -> float:
        """
        Calculate cost for custom endpoint.

        Since pricing varies by provider, return 0.0 by default.
        Can be overridden with custom pricing in config.
        """
        # Check if custom pricing is provided in config
        if "pricing" in self.config:
            pricing = self.config["pricing"]
            input_cost = (prompt_tokens / 1_000_000) * pricing.get("input", 0)
            output_cost = (completion_tokens / 1_000_000) * pricing.get("output", 0)
            return input_cost + output_cost

        return 0.0
