# ════════════════════════════════════════════════════════════════
# InnAgent AI — Dashboard Router
# GET /dashboard/summary, /metrics, /tasks
# ════════════════════════════════════════════════════════════════

from fastapi import APIRouter, HTTPException, Query
from datetime import date, timedelta
from typing import Optional
from backend.database import (
    get_hotel_by_id, get_occupancy_for_date, get_open_ticket_count,
    get_latest_metrics, get_metrics_range, get_recent_agent_logs,
    get_tickets_by_hotel, get_rooms_by_hotel,
    get_conversations_by_hotel, get_conversation_thread
)
from backend.utils.logger import get_logger

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])
logger = get_logger("dashboard_router")


@router.get("/summary/{hotel_id}")
async def get_dashboard_summary(hotel_id: str):
    """Get dashboard KPIs and summary for a hotel."""
    try:
        hotel = get_hotel_by_id(hotel_id)
        if not hotel:
            raise HTTPException(status_code=404, detail="Hotel not found")

        today = date.today()
        occupancy = get_occupancy_for_date(hotel_id, today)
        metrics = get_latest_metrics(hotel_id)
        open_tickets = get_open_ticket_count(hotel_id)
        recent_logs = get_recent_agent_logs(hotel_id, limit=10)

        kpis = {
            "occupancy_rate": occupancy.get("occupancy_rate", 0),
            "adr_lkr": metrics.get("adr_lkr", 0) if metrics else 0,
            "revpar_lkr": metrics.get("revpar_lkr", 0) if metrics else 0,
            "open_tickets": open_tickets,
        }

        return {
            "hotel_id": hotel_id,
            "hotel_name": hotel["name"],
            "kpis": kpis,
            "recent_activity": recent_logs,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Dashboard summary error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics/{hotel_id}")
async def get_hotel_metrics(
    hotel_id: str,
    days: int = Query(default=7, ge=1, le=90),
):
    """Get occupancy and revenue metrics for a date range."""
    try:
        today = date.today()
        start = today - timedelta(days=days)
        metrics = get_metrics_range(hotel_id, start, today)

        # Build occupancy trend
        occupancy_trend = [
            {"date": m["date"], "occupancy": m.get("occupancy_rate", 0)}
            for m in metrics
        ]

        # Build revenue by room type
        rooms = get_rooms_by_hotel(hotel_id)
        revenue_by_room = [
            {"room_type": r["room_type"], "revenue": r.get("base_rate_lkr", 0) * r.get("total_count", 1)}
            for r in rooms
        ]

        return {
            "hotel_id": hotel_id,
            "period_days": days,
            "occupancy_trend": occupancy_trend,
            "revenue_by_room": revenue_by_room,
            "daily_metrics": metrics,
        }
    except Exception as e:
        logger.error(f"Metrics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tasks/{hotel_id}")
async def get_hotel_tasks(
    hotel_id: str,
    status: Optional[str] = None,
):
    """Get maintenance/housekeeping tasks for a hotel."""
    try:
        tickets = get_tickets_by_hotel(hotel_id, status=status)
        return {"hotel_id": hotel_id, "tasks": tickets, "count": len(tickets)}
    except Exception as e:
        logger.error(f"Tasks error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/activity")
async def get_recent_activity(
    hotel_id: Optional[str] = None,
    limit: int = Query(default=10, ge=1, le=50),
):
    """Get recent agent activity across all or specific hotel."""
    try:
        logs = get_recent_agent_logs(hotel_id, limit=limit)
        return {"activity": logs, "count": len(logs)}
    except Exception as e:
        logger.error(f"Activity error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversations/{hotel_id}")
async def get_hotel_conversations(hotel_id: str):
    """Get unique guest conversations and their latest message."""
    try:
        messages = get_conversations_by_hotel(hotel_id, limit=100)
        
        # Group by phone number
        conversations_dict = {}
        for msg in messages:
            phone = msg["guest_phone"]
            if phone not in conversations_dict:
                conversations_dict[phone] = {
                    "guest_phone": phone,
                    "guest_name": msg.get("guest_name"),
                    "last_message": msg["message_body"],
                    "language": msg.get("language", "english"),
                    "timestamp": msg["created_at"],
                    "unread": False,  # Simplified for prototype
                }
                
        # Convert to list and sort by timestamp
        conversations_list = list(conversations_dict.values())
        conversations_list.sort(key=lambda x: x["timestamp"], reverse=True)
        
        return {"conversations": conversations_list}
    except Exception as e:
        logger.error(f"Conversations error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversations/{hotel_id}/{guest_phone}")
async def get_guest_thread(hotel_id: str, guest_phone: str):
    """Get the full message thread for a specific guest."""
    try:
        messages = get_conversation_thread(hotel_id, guest_phone)
        return {"messages": messages}
    except Exception as e:
        logger.error(f"Conversation thread error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
