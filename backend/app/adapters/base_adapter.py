from abc import ABC, abstractmethod
from typing import Dict, List, Optional, AsyncIterator, Any
from pydantic import BaseModel


class ChatMessage(BaseModel):
    """Chat message model"""
    role: str  # system, user, assistant
    content: str


class ChatCompletionResponse(BaseModel):
    """Chat completion response model"""
    content: str
    model: str
    usage: Optional[Dict[str, int]] = None
    finish_reason: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class BaseLLMAdapter(ABC):
    """
    Abstract base class for LLM adapters.

    All LLM provider adapters must inherit from this class and implement
    the required methods.
    """

    def __init__(self, api_key: Optional[str] = None, **kwargs):
        """
        Initialize the adapter.

        Args:
            api_key: API key for the provider (optional for local models)
            **kwargs: Additional configuration parameters
        """
        self.api_key = api_key
        self.config = kwargs

    @abstractmethod
    async def chat(
        self,
        messages: List[ChatMessage],
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> ChatCompletionResponse:
        """
        Send chat completion request.

        Args:
            messages: List of chat messages
            model: Model name
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens to generate
            **kwargs: Additional provider-specific parameters

        Returns:
            ChatCompletionResponse object

        Raises:
            Exception: If the request fails
        """
        pass

    @abstractmethod
    async def stream_chat(
        self,
        messages: List[ChatMessage],
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """
        Send streaming chat completion request.

        Args:
            messages: List of chat messages
            model: Model name
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens to generate
            **kwargs: Additional provider-specific parameters

        Yields:
            Content chunks as they arrive

        Raises:
            Exception: If the request fails
        """
        pass

    @abstractmethod
    async def get_models(self) -> List[str]:
        """
        Get list of available models.

        Returns:
            List of model names

        Raises:
            Exception: If the request fails
        """
        pass

    @abstractmethod
    def validate_config(self) -> bool:
        """
        Validate adapter configuration.

        Returns:
            True if configuration is valid

        Raises:
            ValueError: If configuration is invalid
        """
        pass

    def _format_messages(self, messages: List[ChatMessage]) -> List[Dict[str, str]]:
        """
        Format messages to provider-specific format.

        Args:
            messages: List of ChatMessage objects

        Returns:
            List of message dictionaries
        """
        return [{"role": msg.role, "content": msg.content} for msg in messages]

    def _calculate_cost(
        self,
        model: str,
        prompt_tokens: int,
        completion_tokens: int
    ) -> float:
        """
        Calculate estimated cost for the request.

        Args:
            model: Model name
            prompt_tokens: Number of prompt tokens
            completion_tokens: Number of completion tokens

        Returns:
            Estimated cost in USD
        """
        # This is a simplified cost calculation
        # Should be overridden by specific adapters with accurate pricing
        return 0.0
