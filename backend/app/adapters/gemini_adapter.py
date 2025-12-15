from typing import List, Optional, AsyncIterator
import google.generativeai as genai

from app.adapters.base_adapter import (
    BaseLLMAdapter,
    ChatMessage,
    ChatCompletionResponse
)
from app.core.logger import get_logger

logger = get_logger("gemini_adapter")


class GeminiAdapter(BaseLLMAdapter):
    """Adapter for Google Gemini API"""

    # Pricing per 1M tokens (as of 2024)
    PRICING = {
        "gemini-pro": {"input": 0.5, "output": 1.5},
        "gemini-pro-vision": {"input": 0.5, "output": 1.5},
        "gemini-1.5-pro": {"input": 3.5, "output": 10.5},
        "gemini-1.5-flash": {"input": 0.35, "output": 1.05},
    }

    def __init__(self, api_key: str, **kwargs):
        """
        Initialize Gemini adapter.

        Args:
            api_key: Google API key
            **kwargs: Additional configuration
        """
        super().__init__(api_key, **kwargs)
        genai.configure(api_key=api_key)
        logger.info("Gemini adapter initialized")

    def _convert_messages(self, messages: List[ChatMessage]) -> List[dict]:
        """
        Convert messages to Gemini format.

        Gemini uses 'user' and 'model' roles instead of 'assistant'.
        """
        gemini_messages = []

        for msg in messages:
            if msg.role == "system":
                # Gemini doesn't have system role, prepend to first user message
                continue
            role = "model" if msg.role == "assistant" else "user"
            gemini_messages.append({
                "role": role,
                "parts": [msg.content]
            })

        return gemini_messages

    async def chat(
        self,
        messages: List[ChatMessage],
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> ChatCompletionResponse:
        """Send chat completion request to Gemini."""
        try:
            model_instance = genai.GenerativeModel(model)

            # Extract system message if present
            system_instruction = None
            chat_messages = []
            for msg in messages:
                if msg.role == "system":
                    system_instruction = msg.content
                else:
                    chat_messages.append(msg)

            # Build generation config
            generation_config = {
                "temperature": temperature,
            }
            if max_tokens:
                generation_config["max_output_tokens"] = max_tokens

            # Convert messages
            gemini_messages = self._convert_messages(chat_messages)

            # Start chat
            chat = model_instance.start_chat(history=gemini_messages[:-1])

            # Send last message
            response = await chat.send_message_async(
                gemini_messages[-1]["parts"][0],
                generation_config=generation_config
            )

            content = response.text

            # Gemini doesn't provide detailed usage info in the same way
            usage = {
                "prompt_tokens": 0,  # Not provided
                "completion_tokens": 0,  # Not provided
                "total_tokens": 0,
            }

            logger.info(f"Gemini chat completed: model={model}")

            return ChatCompletionResponse(
                content=content,
                model=model,
                usage=usage,
                finish_reason="stop",
                metadata={}
            )

        except Exception as e:
            logger.error(f"Gemini chat error: {str(e)}")
            raise

    async def stream_chat(
        self,
        messages: List[ChatMessage],
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """Send streaming chat completion request to Gemini."""
        try:
            model_instance = genai.GenerativeModel(model)

            chat_messages = [msg for msg in messages if msg.role != "system"]
            gemini_messages = self._convert_messages(chat_messages)

            generation_config = {
                "temperature": temperature,
            }
            if max_tokens:
                generation_config["max_output_tokens"] = max_tokens

            chat = model_instance.start_chat(history=gemini_messages[:-1])

            logger.info(f"Gemini stream chat started: model={model}")

            response = await chat.send_message_async(
                gemini_messages[-1]["parts"][0],
                generation_config=generation_config,
                stream=True
            )

            async for chunk in response:
                if chunk.text:
                    yield chunk.text

        except Exception as e:
            logger.error(f"Gemini stream chat error: {str(e)}")
            raise

    async def get_models(self) -> List[str]:
        """Get list of available Gemini models."""
        try:
            models = genai.list_models()
            model_names = [
                model.name.replace("models/", "")
                for model in models
                if "generateContent" in model.supported_generation_methods
            ]
            logger.info(f"Retrieved {len(model_names)} Gemini models")
            return model_names
        except Exception as e:
            logger.error(f"Failed to get Gemini models: {str(e)}")
            raise

    def validate_config(self) -> bool:
        """Validate Gemini adapter configuration."""
        if not self.api_key:
            raise ValueError("Google API key is required")
        return True

    def _calculate_cost(
        self,
        model: str,
        prompt_tokens: int,
        completion_tokens: int
    ) -> float:
        """Calculate estimated cost for Gemini request."""
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
