# ════════════════════════════════════════════════════════════════
# InnAgent AI — Routers Package Init
# ════════════════════════════════════════════════════════════════

from backend.routers.agent_router import router as agent_router
from backend.routers.webhook_router import router as webhook_router
from backend.routers.dashboard_router import router as dashboard_router
from backend.routers.hotels_router import router as hotels_router
from backend.routers.reviews_router import router as reviews_router

__all__ = [
    "agent_router",
    "webhook_router",
    "dashboard_router",
    "hotels_router",
    "reviews_router",
]
