from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.adapters.adapter_factory import AdapterFactory
from app.services.api_key_service import APIKeyService
from app.models.user import User

router = APIRouter()


@router.get("/providers")
async def get_supported_providers():
    """
    Get list of supported LLM providers.

    Returns list of provider names that can be configured.
    """
    providers = AdapterFactory.get_supported_providers()
    return {"providers": providers}


@router.get("/{api_key_id}/models")
async def get_models_for_api_key(
    api_key_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get available models for a specific API key.

    This fetches the model list from the provider using the configured API key.
    """
    # Get API key
    api_key = APIKeyService.get_api_key(db, api_key_id, current_user.id)

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )

    if not api_key.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="API key is not active"
        )

    try:
        # Create adapter and get models
        adapter = AdapterFactory.create_adapter_from_db(api_key)
        models = await adapter.get_models()

        return {
            "provider": api_key.provider,
            "api_key_id": api_key_id,
            "models": models
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch models: {str(e)}"
        )


@router.get("/provider/{provider}/models")
async def get_models_by_provider_type(provider: str):
    """
    Get known models for a provider type.

    This returns hardcoded model lists for common providers.
    For actual available models, use /{api_key_id}/models endpoint.
    """
    # Known models by provider
    known_models = {
        "openai": [
            "gpt-4",
            "gpt-4-turbo",
            "gpt-4o",
            "gpt-4o-mini",
            "gpt-3.5-turbo"
        ],
        "claude": [
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307",
            "claude-3-5-sonnet-20241022"
        ],
        "anthropic": [
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307",
            "claude-3-5-sonnet-20241022"
        ],
        "gemini": [
            "gemini-pro",
            "gemini-pro-vision",
            "gemini-1.5-pro",
            "gemini-1.5-flash"
        ],
        "google": [
            "gemini-pro",
            "gemini-pro-vision",
            "gemini-1.5-pro",
            "gemini-1.5-flash"
        ],
        "ollama": [
            "llama3",
            "llama3:70b",
            "mistral",
            "mixtral",
            "qwen2",
            "gemma2",
            "phi3"
        ]
    }

    provider_lower = provider.lower()
    if provider_lower not in known_models:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Unknown provider: {provider}"
        )

    return {
        "provider": provider,
        "models": known_models[provider_lower],
        "note": "These are known models. Actual availability may vary. Use /{api_key_id}/models for accurate list."
    }
