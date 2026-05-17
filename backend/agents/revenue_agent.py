# ════════════════════════════════════════════════════════════════
# InnAgent AI — Revenue Agent
# RevPAR, ADR, occupancy analytics
# ════════════════════════════════════════════════════════════════

import json
from datetime import date, timedelta
from backend.config import get_settings
from backend.services.groq_service import call_groq, build_agent_prompt
from backend.utils.logger import get_logger

settings = get_settings()
logger = get_logger("revenue_agent")

REVENUE_SUB_PROMPT = """You are the RevenueAgent for {hotel_name}.
Your job: Calculate KPIs and generate performance summaries.

Given raw data, calculate:
- Occupancy Rate = (rooms_sold / total_rooms) * 100
- ADR = total_room_revenue / rooms_sold
- RevPAR = ADR * (occupancy_rate / 100)
- Direct Booking % = (direct_bookings / total_bookings) * 100

Output in "data" field:
{{
  "occupancy_rate": number,
  "adr_lkr": number,
  "revpar_lkr": number,
  "direct_booking_pct": number,
  "top_issue": string,
  "top_opportunity": string,
  "trend": "improving" | "stable" | "declining",
  "benchmark_vs_target": {{
    "occupancy": "above" | "below" | "on_target",
    "revpar": "above" | "below" | "on_target"
  }}
}}

TARGETS: Occupancy > 72% | ADR: track vs comp | Direct booking > 35%"""


class RevenueAgent:
    """Revenue analytics and KPI calculation agent."""

    agent_name = "revenue_agent"

    async def run(self, task: str, hotel_profile: dict, context: dict = None) -> dict:
        context = context or {}
        hotel_name = hotel_profile.get("hotel_name", "Unknown Hotel")
        metrics = hotel_profile.get("latest_metrics")
        occupancy_data = hotel_profile.get("current_occupancy", {})

        # Build metrics summary
        bookings = context.get("bookings", [])
        total_rooms = hotel_profile.get("total_rooms", 0)
        rooms_sold = occupancy_data.get("rooms_sold", 0)
        total_revenue = context.get("total_revenue_lkr", 0)
        direct_bookings = context.get("direct_bookings", 0)
        total_bookings = context.get("total_bookings", 0)

        user_message = (
            f"Task: {task}\n"
            f"Hotel: {hotel_name}\n"
            f"Total rooms: {total_rooms}\n"
            f"Rooms sold today: {rooms_sold}\n"
            f"Total revenue (period): LKR {total_revenue:,}\n"
            f"Direct bookings: {direct_bookings}\n"
            f"Total bookings: {total_bookings}\n"
        )

        if metrics:
            user_message += f"Latest daily metrics: {json.dumps(metrics)}\n"

        sub_prompt = REVENUE_SUB_PROMPT.format(hotel_name=hotel_name)
        system_prompt = build_agent_prompt(settings.BASE_SYSTEM_PROMPT, sub_prompt, hotel_profile)

        try:
            result = await call_groq(system_prompt, user_message)
            result.setdefault("agent_used", self.agent_name)
            result.setdefault("confidence", 0.85)
            result.setdefault("escalate_to_human", False)
            logger.info(f"Revenue analysis generated for {hotel_name}")
            return result
        except Exception as e:
            logger.error(f"RevenueAgent error for {hotel_name}: {e}")
            return self._fallback_response(hotel_name, total_rooms, rooms_sold, total_revenue, direct_bookings, total_bookings, str(e))

    def _fallback_response(self, hotel_name, total_rooms, rooms_sold, revenue, direct, total_bk, error):
        """Calculate KPIs directly when LLM is unavailable."""
        occupancy = (rooms_sold / total_rooms * 100) if total_rooms > 0 else 0
        adr = (revenue // rooms_sold) if rooms_sold > 0 else 0
        revpar = int(adr * occupancy / 100) if adr > 0 else 0
        direct_pct = (direct / total_bk * 100) if total_bk > 0 else 0

        occ_status = "above" if occupancy > 72 else ("on_target" if occupancy >= 68 else "below")
        trend = "improving" if occupancy > 72 else ("stable" if occupancy > 55 else "declining")

        return {
            "agent_used": self.agent_name,
            "action_taken": "kpi_calculation_fallback",
            "output": f"KPIs calculated for {hotel_name}: Occ {occupancy:.1f}%, ADR LKR {adr:,}, RevPAR LKR {revpar:,}",
            "confidence": 0.7,
            "escalate_to_human": False,
            "escalation_reason": None,
            "follow_up_suggested": "Review KPIs and set action items" if occupancy < 60 else None,
            "data": {
                "occupancy_rate": round(occupancy, 1),
                "adr_lkr": adr,
                "revpar_lkr": revpar,
                "direct_booking_pct": round(direct_pct, 1),
                "top_issue": "Low occupancy" if occupancy < 60 else "Revenue optimization needed" if adr < 15000 else "On track",
                "top_opportunity": "Increase direct bookings" if direct_pct < 35 else "Optimize pricing",
                "trend": trend,
                "benchmark_vs_target": {"occupancy": occ_status, "revpar": "below" if revpar < 10000 else "above"},
            },
        }
