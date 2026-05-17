# ════════════════════════════════════════════════════════════════
# InnAgent AI — LangGraph Orchestrator
# Routes tasks to the appropriate agent
# ════════════════════════════════════════════════════════════════

import time
import json
from typing import Optional
from backend.agents.pricing_agent import PricingAgent
from backend.agents.guest_bot import GuestBot
from backend.agents.revenue_agent import RevenueAgent
from backend.agents.review_agent import ReviewAgent
from backend.agents.operations_agent import OperationsAgent
from backend.database import build_hotel_profile, save_agent_log
from backend.utils.logger import get_logger

logger = get_logger("orchestrator")

# Agent instances
_agents = {
    "pricing_agent": PricingAgent(),
    "guest_bot": GuestBot(),
    "revenue_agent": RevenueAgent(),
    "review_agent": ReviewAgent(),
    "operations_agent": OperationsAgent(),
}

# Task-to-agent routing rules
TASK_ROUTING = {
    # Pricing tasks
    "daily_pricing_check": "pricing_agent",
    "pricing_recommendation": "pricing_agent",
    "rate_adjustment": "pricing_agent",
    "competitor_analysis": "pricing_agent",
    # Guest communication
    "guest_message": "guest_bot",
    "whatsapp_reply": "guest_bot",
    "guest_inquiry": "guest_bot",
    # Revenue analytics
    "revenue_report": "revenue_agent",
    "kpi_calculation": "revenue_agent",
    "performance_summary": "revenue_agent",
    "daily_metrics": "revenue_agent",
    # Review management
    "daily_review_scan": "review_agent",
    "review_response": "review_agent",
    "review_draft": "review_agent",
    # Operations
    "daily_housekeeping_tasks": "operations_agent",
    "maintenance_ticket": "operations_agent",
    "housekeeping_schedule": "operations_agent",
    "inspection_task": "operations_agent",
}


def route_task(task: str, agent_type: Optional[str] = None) -> str:
    """Determine which agent should handle a task."""
    # If agent explicitly specified, use it
    if agent_type and agent_type in _agents:
        return agent_type

    # Check exact match in routing table
    task_lower = task.lower().strip()
    if task_lower in TASK_ROUTING:
        return TASK_ROUTING[task_lower]

    # Keyword-based routing
    keywords = {
        "pricing_agent": ["price", "pricing", "rate", "tariff", "cost", "competitor", "discount"],
        "guest_bot": ["guest", "message", "whatsapp", "inquiry", "booking request", "reservation", "check-in", "check-out"],
        "revenue_agent": ["revenue", "kpi", "occupancy", "adr", "revpar", "performance", "analytics", "metric"],
        "review_agent": ["review", "feedback", "rating", "complaint", "tripadvisor", "booking.com review"],
        "operations_agent": ["housekeeping", "maintenance", "cleaning", "repair", "task", "inspection", "staff"],
    }

    for agent_name, words in keywords.items():
        for word in words:
            if word in task_lower:
                return agent_name

    # Default to guest bot for unrecognized tasks
    logger.warning(f"No routing match for task: '{task}', defaulting to guest_bot")
    return "guest_bot"


async def run_orchestrator(
    task: str,
    hotel_id: str,
    agent_type: Optional[str] = None,
    context: dict = None,
) -> dict:
    """
    Main orchestrator: route task to appropriate agent and execute.
    Logs all agent runs to the database.
    """
    context = context or {}
    start_time = time.time()

    # Build hotel profile
    try:
        hotel_profile = build_hotel_profile(hotel_id)
        if not hotel_profile:
            return {
                "agent_used": "orchestrator",
                "action_taken": "hotel_not_found",
                "output": f"Hotel {hotel_id} not found or inactive",
                "confidence": 0.0,
                "escalate_to_human": True,
                "escalation_reason": "Hotel profile not found",
                "data": None,
            }
    except Exception as e:
        logger.warning(f"Could not build hotel profile: {e}. Using empty profile.")
        hotel_profile = {"hotel_id": hotel_id, "hotel_name": "Unknown", "rooms": [], "total_rooms": 0}

    # Route to agent
    selected_agent = route_task(task, agent_type)
    agent = _agents.get(selected_agent)

    if not agent:
        return {
            "agent_used": "orchestrator",
            "action_taken": "agent_not_found",
            "output": f"Agent '{selected_agent}' not found",
            "confidence": 0.0,
            "escalate_to_human": True,
            "escalation_reason": f"Unknown agent: {selected_agent}",
            "data": None,
        }

    logger.info(f"Routing task '{task}' to {selected_agent} for hotel {hotel_id}")

    # Execute agent
    try:
        result = await agent.run(task, hotel_profile, context)
    except Exception as e:
        logger.error(f"Agent execution error: {e}", exc_info=True)
        result = {
            "agent_used": selected_agent,
            "action_taken": "execution_error",
            "output": f"Agent execution failed: {str(e)}",
            "confidence": 0.0,
            "escalate_to_human": True,
            "escalation_reason": f"Agent error: {str(e)}",
            "data": None,
        }

    elapsed_ms = int((time.time() - start_time) * 1000)

    # Log to database
    try:
        meta = result.get("_meta", {})
        save_agent_log({
            "hotel_id": hotel_id,
            "agent_name": result.get("agent_used", selected_agent),
            "task": task[:500],
            "input_data": {"context_keys": list(context.keys())} if context else None,
            "output_data": {
                "action": result.get("action_taken"),
                "confidence": result.get("confidence"),
                "escalated": result.get("escalate_to_human", False),
            },
            "confidence": result.get("confidence"),
            "escalated": result.get("escalate_to_human", False),
            "escalation_reason": result.get("escalation_reason"),
            "execution_time_ms": elapsed_ms,
            "tokens_used": meta.get("tokens_used", 0),
        })
    except Exception as e:
        logger.warning(f"Failed to log agent run: {e}")

    # Clean up internal meta before returning
    result.pop("_meta", None)

    return result
