# ════════════════════════════════════════════════════════════════
# InnAgent AI — Agents Package Init
# ════════════════════════════════════════════════════════════════

from backend.agents.pricing_agent import PricingAgent
from backend.agents.guest_bot import GuestBot
from backend.agents.revenue_agent import RevenueAgent
from backend.agents.review_agent import ReviewAgent
from backend.agents.operations_agent import OperationsAgent

AGENT_REGISTRY = {
    "pricing_agent": PricingAgent,
    "guest_bot": GuestBot,
    "revenue_agent": RevenueAgent,
    "review_agent": ReviewAgent,
    "operations_agent": OperationsAgent,
}

__all__ = [
    "PricingAgent",
    "GuestBot",
    "RevenueAgent",
    "ReviewAgent",
    "OperationsAgent",
    "AGENT_REGISTRY",
]
