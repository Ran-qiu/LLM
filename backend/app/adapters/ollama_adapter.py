from typing import List, Optional, AsyncIterator
import ollama

from app.adapters.base_adapter import (
    BaseLLMAdapter,
    ChatMessage,
    ChatCompletionResponse
)
from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger("ollama_adapter")


class OllamaAdapter(BaseLLMAdapter):
    """Adapter for Ollama local models"""

    def __init__(self, base_url: Optional[str] = None, **kwargs):
        """
        Initialize Ollama adapter.

        Args:
            base_url: Ollama server URL (default: from settings)
            **kwargs: Additional configuration
        """
        super().__init__(api_key=None, **kwargs)  # Ollama doesn't need API key
        self.base_url = base_url or settings.OLLAMA_BASE_URL
        self.client = ollama.AsyncClient(host=self.base_url)
        logger.info(f"Ollama adapter initialized: {self.base_url}")

    async def chat(
        self,
        messages: List[ChatMessage],
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> ChatCompletionResponse:
        """Send chat completion request to Ollama."""
        try:
            formatted_messages = self._format_messages(messages)

            options = {
                "temperature": temperature,
            }
            if max_tokens:
                options["num_predict"] = max_tokens

            response = await self.client.chat(
                model=model,
                messages=formatted_messages,
                options=options,
                **kwargs
            )

            content = response["message"]["content"]

            # Ollama provides token counts
            usage = None
            if "prompt_eval_count" in response:
                usage = {
                    "prompt_tokens": response.get("prompt_eval_count", 0),
                    "completion_tokens": response.get("eval_count", 0),
                    "total_tokens": response.get("prompt_eval_count", 0) + response.get("eval_count", 0),
                }

            logger.info(
                f"Ollama chat completed: model={model}, "
                f"tokens={usage['total_tokens'] if usage else 'unknown'}"
            )

            return ChatCompletionResponse(
                content=content,
                model=model,
                usage=usage,
                finish_reason="stop",
                metadata={
                    "eval_duration": response.get("eval_duration"),
                    "load_duration": response.get("load_duration"),
                }
            )

        except Exception as e:
            logger.error(f"Ollama chat error: {str(e)}")
            raise

    async def stream_chat(
        self,
        messages: List[ChatMessage],
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """Send streaming chat completion request to Ollama."""
        try:
            formatted_messages = self._format_messages(messages)

            options = {
                "temperature": temperature,
            }
            if max_tokens:
                options["num_predict"] = max_tokens

            logger.info(f"Ollama stream chat started: model={model}")

            stream = await self.client.chat(
                model=model,
                messages=formatted_messages,
                options=options,
                stream=True,
                **kwargs
            )

            async for chunk in stream:
                if "message" in chunk and "content" in chunk["message"]:
                    yield chunk["message"]["content"]

        except Exception as e:
            logger.error(f"Ollama stream chat error: {str(e)}")
            raise

    async def get_models(self) -> List[str]:
        """Get list of available Ollama models."""
        try:
            response = await self.client.list()
            models = [model["name"] for model in response.get("models", [])]
            logger.info(f"Retrieved {len(models)} Ollama models")
            return models
        except Exception as e:
            logger.error(f"Failed to get Ollama models: {str(e)}")
            raise

    def validate_config(self) -> bool:
        """Validate Ollama adapter configuration."""
        if not self.base_url:
            raise ValueError("Ollama base URL is required")
        return True

    async def pull_model(self, model: str) -> bool:
        """
        Pull a model from Ollama registry.

        Args:
            model: Model name to pull

        Returns:
            True if successful

        Raises:
            Exception: If pull fails
        """
        try:
            logger.info(f"Pulling Ollama model: {model}")
            await self.client.pull(model)
            logger.info(f"Successfully pulled model: {model}")
            return True
        except Exception as e:
            logger.error(f"Failed to pull model {model}: {str(e)}")
            raise

    async def delete_model(self, model: str) -> bool:
        """
        Delete a model from Ollama.

        Args:
            model: Model name to delete

        Returns:
            True if successful

        Raises:
            Exception: If delete fails
        """
        try:
            logger.info(f"Deleting Ollama model: {model}")
            await self.client.delete(model)
            logger.info(f"Successfully deleted model: {model}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete model {model}: {str(e)}")
            raise

    def _calculate_cost(
        self,
        model: str,
        prompt_tokens: int,
        completion_tokens: int
    ) -> float:
        """Calculate cost for Ollama request (always 0 for local models)."""
        return 0.0
