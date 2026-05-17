# ════════════════════════════════════════════════════════════════
# InnAgent AI — Agent Router
# POST /agent/run — main orchestrator endpoint
# ════════════════════════════════════════════════════════════════

from fastapi import APIRouter, HTTPException, Header
from typing import Optional
from backend.models import AgentRequest, AgentResponse
from backend.agents.orchestrator import run_orchestrator
from backend.config import get_settings
from backend.utils.logger import get_logger

router = APIRouter(prefix="/agent", tags=["Agent"])
logger = get_logger("agent_router")
settings = get_settings()


def verify_api_key(api_key: Optional[str] = None):
    """Verify API key for scheduled/external calls."""
    if settings.INNAGENT_API_KEY and api_key:
        if api_key != settings.INNAGENT_API_KEY:
            raise HTTPException(status_code=401, detail="Invalid API key")


@router.post("/run", response_model=AgentResponse)
async def run_agent(
    request: AgentRequest,
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
):
    """
    Run the AI agent orchestrator with a task.
    Routes to the appropriate agent based on task content.
    """
    # Verify API key if provided (optional for dev, required for cron)
    if x_api_key:
        verify_api_key(x_api_key)

    if not request.hotel_id:
        raise HTTPException(status_code=400, detail="hotel_id is required")

    logger.info(f"Agent run requested: task='{request.task}', hotel={request.hotel_id}")

    try:
        result = await run_orchestrator(
            task=request.task,
            hotel_id=request.hotel_id,
            agent_type=request.agent_type.value if request.agent_type else None,
            context=request.context,
        )
        return AgentResponse(**result)
    except Exception as e:
        logger.error(f"Agent run failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Agent execution failed: {str(e)}")


@router.post("/batch")
async def run_agent_batch(
    tasks: list[AgentRequest],
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
):
    """Run multiple agent tasks in sequence (for cron jobs)."""
    if x_api_key:
        verify_api_key(x_api_key)

    results = []
    for req in tasks:
        try:
            result = await run_orchestrator(
                task=req.task,
                hotel_id=req.hotel_id or "",
                agent_type=req.agent_type.value if req.agent_type else None,
                context=req.context,
            )
            results.append({"hotel_id": req.hotel_id, "status": "success", "result": result})
        except Exception as e:
            results.append({"hotel_id": req.hotel_id, "status": "error", "error": str(e)})

    return {"results": results, "total": len(results)}
