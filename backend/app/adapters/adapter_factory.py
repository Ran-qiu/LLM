from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from app.adapters.base_adapter import BaseLLMAdapter
from app.adapters.openai_adapter import OpenAIAdapter
from app.adapters.claude_adapter import ClaudeAdapter
from app.adapters.gemini_adapter import GeminiAdapter
from app.adapters.ollama_adapter import OllamaAdapter
from app.adapters.custom_adapter import CustomAdapter
from app.models.api_key import APIKey
from app.core.security import decrypt_api_key
from app.core.logger import get_logger

logger = get_logger("adapter_factory")


class AdapterFactory:
    """Factory for creating LLM adapters based on provider"""

    @staticmethod
    def create_adapter(
        provider: str,
        api_key: Optional[str] = None,
        custom_config: Optional[Dict[str, Any]] = None
    ) -> BaseLLMAdapter:
        """
        Create an LLM adapter based on provider type.

        Args:
            provider: Provider name (openai, claude, gemini, ollama, custom)
            api_key: API key for the provider
            custom_config: Custom configuration for the adapter

        Returns:
            Adapter instance

        Raises:
            ValueError: If provider is not supported
        """
        provider_lower = provider.lower()

        try:
            if provider_lower == "openai":
                if not api_key:
                    raise ValueError("OpenAI requires an API key")
                base_url = custom_config.get("base_url") if custom_config else None
                return OpenAIAdapter(api_key=api_key, base_url=base_url)

            elif provider_lower == "claude" or provider_lower == "anthropic":
                if not api_key:
                    raise ValueError("Claude requires an API key")
                return ClaudeAdapter(api_key=api_key)

            elif provider_lower == "gemini" or provider_lower == "google":
                if not api_key:
                    raise ValueError("Gemini requires an API key")
                return GeminiAdapter(api_key=api_key)

            elif provider_lower == "ollama":
                base_url = None
                if custom_config and "base_url" in custom_config:
                    base_url = custom_config["base_url"]
                return OllamaAdapter(base_url=base_url)

            elif provider_lower == "custom":
                if not api_key:
                    raise ValueError("Custom adapter requires an API key")
                if not custom_config or "base_url" not in custom_config:
                    raise ValueError("Custom adapter requires base_url in config")

                return CustomAdapter(
                    api_key=api_key,
                    base_url=custom_config["base_url"],
                    model_type=custom_config.get("model_type", "openai-compatible"),
                    **custom_config
                )

            else:
                raise ValueError(f"Unsupported provider: {provider}")

        except Exception as e:
            logger.error(f"Failed to create adapter for {provider}: {str(e)}")
            raise

    @staticmethod
    def create_adapter_from_db(db_api_key: APIKey) -> BaseLLMAdapter:
        """
        Create an adapter from database APIKey model.

        Args:
            db_api_key: APIKey database model

        Returns:
            Adapter instance
        """
        # Decrypt API key if present
        decrypted_key = None
        if db_api_key.encrypted_key:
            decrypted_key = decrypt_api_key(db_api_key.encrypted_key)

        # Create adapter
        adapter = AdapterFactory.create_adapter(
            provider=db_api_key.provider,
            api_key=decrypted_key,
            custom_config=db_api_key.custom_config
        )

        logger.info(
            f"Created adapter from DB: provider={db_api_key.provider}, "
            f"name={db_api_key.name}"
        )

        return adapter

    @staticmethod
    def get_supported_providers() -> list[str]:
        """Get list of supported providers."""
        return ["openai", "claude", "anthropic", "gemini", "google", "ollama", "custom"]
