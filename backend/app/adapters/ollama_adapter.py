from typing import List, Optional, AsyncIterator
from openai import AsyncOpenAI

from app.adapters.base_adapter import (
    BaseLLMAdapter,
    ChatMessage,
    ChatCompletionResponse
)
from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger("ollama_adapter")


class OllamaAdapter(BaseLLMAdapter):
    """
    Adapter for Ollama local models using OpenAI-compatible SDK.
    
    This provides better consistency and unified handling for all 
    OpenAI-compatible local and remote services.
    """

    def __init__(self, base_url: Optional[str] = None, **kwargs):
        """
        Initialize Ollama adapter.

        Args:
            base_url: Ollama server URL (default: from settings)
            **kwargs: Additional configuration
        """
        # Ollama doesn't need a real API key for local usage, but OpenAI SDK requires one
        super().__init__(api_key="ollama", **kwargs)
        
        # Ensure base_url ends with /v1 for OpenAI SDK compatibility
        raw_url = base_url or settings.OLLAMA_BASE_URL
        if not raw_url.endswith('/v1'):
            self.base_url = f"{raw_url.rstrip('/')}/v1"
        else:
            self.base_url = raw_url

        self.client = AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
        logger.info(f"Ollama adapter initialized via OpenAI SDK: {self.base_url}")

    async def chat(
        self,
        messages: List[ChatMessage],
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> ChatCompletionResponse:
        """Send chat completion request to Ollama via OpenAI SDK."""
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

            # Extract usage info
            usage = None
            if response.usage:
                usage = {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                }

            logger.info(
                f"Ollama(OpenAI) chat completed: model={model}, "
                f"tokens={usage['total_tokens'] if usage else 'unknown'}"
            )

            return ChatCompletionResponse(
                content=content,
                model=model,
                usage=usage,
                finish_reason=response.choices[0].finish_reason,
                metadata={
                    "base_url": self.base_url
                }
            )

        except Exception as e:
            logger.error(f"Ollama(OpenAI) chat error: {str(e)}")
            raise

    async def stream_chat(
        self,
        messages: List[ChatMessage],
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """Send streaming chat completion request to Ollama via OpenAI SDK."""
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

            logger.info(f"Ollama(OpenAI) stream chat started: model={model}")

            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            logger.error(f"Ollama(OpenAI) stream chat error: {str(e)}")
            raise

    async def get_models(self) -> List[str]:
        """Get list of available Ollama models via OpenAI SDK."""
        try:
            # Note: Not all Ollama versions support /v1/models yet
            response = await self.client.models.list()
            models = [model.id for model in response.data]
            logger.info(f"Retrieved {len(models)} Ollama models")
            return models
        except Exception as e:
            logger.warning(f"Failed to get Ollama models via /v1/models: {str(e)}")
            # Fallback or return empty list
            return []

    def validate_config(self) -> bool:
        """Validate Ollama adapter configuration."""
        if not self.base_url:
            raise ValueError("Ollama base URL is required")
        return True

    def _calculate_cost(
        self,
        model: str,
        prompt_tokens: int,
        completion_tokens: int
    ) -> float:
        """Calculate cost for Ollama request (always 0 for local models)."""
        return 0.0