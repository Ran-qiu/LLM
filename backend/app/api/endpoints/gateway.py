from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Union, Dict, Any

from app.core.database import get_db
from app.models.api_key import APIKey
from app.services.llm_service import LLMService
from app.adapters.adapter_factory import AdapterFactory
from app.adapters.base_adapter import ChatMessage
from app.core.security import decrypt_api_key

router = APIRouter()

class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[Dict[str, str]]
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = None
    stream: Optional[bool] = False

async def verify_gateway_key(
    authorization: str = Header(None),
    db: Session = Depends(get_db)
) -> APIKey:
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid Authorization scheme")
    
    # Find key in DB (provider='gateway_client')
    # Since keys are encrypted, this is inefficient (we have to decrypt all to check).
    # BUT, for this project, let's assume we store the gateway client key 
    # in the 'encrypted_key' field PLAIN TEXT (or simple identifier) 
    # to avoid scanning all.
    # OR: we assume the token IS the 'encrypted_key' value (if unique).
    
    # Better approach for this specific requirement without changing schema too much:
    # We search by name/provider and filter? No.
    # Let's verify by checking if the token matches any active 'gateway_client' key.
    # THIS IS SLOW. 
    # Optimization: Store a Hash in 'name' or 'custom_config'?
    
    # Let's rely on finding by token if possible. 
    # For now, simplistic loop (assuming few keys).
    keys = db.query(APIKey).filter(
        APIKey.provider == 'gateway_client',
        APIKey.is_active == True
    ).all()
    
    for key in keys:
        try:
            decrypted = decrypt_api_key(key.encrypted_key)
            if decrypted == token:
                return key
        except:
            continue
            
    raise HTTPException(status_code=401, detail="Invalid API Key")

@router.post("/chat/completions")
async def chat_completions(
    request: ChatCompletionRequest,
    current_key: APIKey = Depends(verify_gateway_key),
    db: Session = Depends(get_db)
):
    """
    OpenAI-compatible chat completions endpoint.
    """
    # 1. Determine upstream provider/model based on request.model
    # Simple mapping logic:
    # "gpt-*" -> openai
    # "claude-*" -> claude
    # "gemini-*" -> gemini
    # else -> ollama (or local)
    
    provider = "ollama"
    if request.model.startswith("gpt"):
        provider = "openai"
    elif request.model.startswith("claude"):
        provider = "anthropic"  # 'anthropic' matches frontend value
    elif request.model.startswith("gemini"):
        provider = "google"     # 'google' matches frontend value
    
    # 2. Find an available upstream key
    # Use the pool logic from LLMService, but we need to adapt it 
    # since LLMService expects a 'conversation' for some context.
    # We'll call get_available_key directly.
    
    # We need a user_id. Use the owner of the gateway key.
    user_id = current_key.user_id
    
    upstream_key = LLMService.get_available_key(db, provider, user_id, -1) # -1 as dummy ID
    
    if not upstream_key and provider == "ollama":
        # Ollama might not need a key, but we need a config.
        # Check if there is a 'ollama' key configured, if not, try default local?
        # For now, require configuration.
        pass
        
    if not upstream_key:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"No available upstream capacity for provider '{provider}'"
        )
        
    # 3. Create adapter and call
    try:
        adapter = AdapterFactory.create_adapter_from_db(upstream_key)
        
        # Convert dict messages to ChatMessage objects
        chat_messages = [
            ChatMessage(role=m["role"], content=m["content"]) 
            for m in request.messages
        ]
        
        if request.stream:
            # Handle streaming
            from fastapi.responses import StreamingResponse
            
            async def event_generator():
                async for chunk in adapter.stream_chat(
                    messages=chat_messages,
                    model=request.model,
                    temperature=request.temperature,
                    max_tokens=request.max_tokens
                ):
                    # Format as SSE (OpenAI style)
                    import json
                    data = json.dumps({
                        "id": "chatcmpl-" + "gateway",
                        "object": "chat.completion.chunk",
                        "created": 0,
                        "model": request.model,
                        "choices": [{"delta": {"content": chunk}, "index": 0, "finish_reason": None}]
                    })
                    yield f"data: {data}\n\n"
                
                yield "data: [DONE]\n\n"

            return StreamingResponse(event_generator(), media_type="text/event-stream")
            
        else:
            # Non-streaming
            response = await adapter.chat(
                messages=chat_messages,
                model=request.model,
                temperature=request.temperature,
                max_tokens=request.max_tokens
            )
            
            return {
                "id": "chatcmpl-" + "gateway",
                "object": "chat.completion",
                "created": 0,
                "model": request.model,
                "choices": [{
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": response.content
                    },
                    "finish_reason": "stop"
                }],
                "usage": response.usage
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))