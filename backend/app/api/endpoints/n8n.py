from fastapi import APIRouter

router = APIRouter()


@router.post("/chat")
async def n8n_chat():
    """Trigger n8n chat workflow - To be implemented"""
    # TODO: Implement n8n chat workflow
    return {"message": "n8n chat endpoint - Coming soon"}


@router.post("/batch-chat")
async def n8n_batch_chat():
    """Trigger n8n batch chat workflow - To be implemented"""
    # TODO: Implement n8n batch chat workflow
    return {"message": "n8n batch chat endpoint - Coming soon"}


@router.get("/workflows")
async def get_workflows():
    """Get available n8n workflows - To be implemented"""
    # TODO: Implement get workflows
    return {"message": "Get n8n workflows endpoint - Coming soon"}


@router.post("/workflows/{workflow_id}/trigger")
async def trigger_workflow(workflow_id: str):
    """Trigger specific n8n workflow - To be implemented"""
    # TODO: Implement trigger workflow
    return {"message": f"Trigger workflow {workflow_id} endpoint - Coming soon"}
