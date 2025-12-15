from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def get_available_models():
    """Get list of available LLM models - To be implemented"""
    # TODO: Implement get available models
    return {"message": "Get models endpoint - Coming soon"}


@router.get("/{provider}")
async def get_models_by_provider(provider: str):
    """Get models for specific provider - To be implemented"""
    # TODO: Implement get models by provider
    return {"message": f"Get {provider} models endpoint - Coming soon"}
