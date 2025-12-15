from fastapi import APIRouter

router = APIRouter()


@router.post("/")
async def create_chat():
    """Create new chat session - To be implemented"""
    # TODO: Implement create chat
    return {"message": "Create chat endpoint - Coming soon"}


@router.post("/message")
async def send_message():
    """Send message to LLM - To be implemented"""
    # TODO: Implement send message
    return {"message": "Send message endpoint - Coming soon"}


@router.get("/history")
async def get_chat_history():
    """Get chat history - To be implemented"""
    # TODO: Implement get chat history
    return {"message": "Get chat history endpoint - Coming soon"}


@router.get("/{conversation_id}")
async def get_conversation(conversation_id: str):
    """Get specific conversation - To be implemented"""
    # TODO: Implement get conversation
    return {"message": f"Get conversation {conversation_id} endpoint - Coming soon"}
