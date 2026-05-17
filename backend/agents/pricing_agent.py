# ════════════════════════════════════════════════════════════════
# InnAgent AI — Pricing Agent
# Dynamic pricing recommendations with peak season logic
# ════════════════════════════════════════════════════════════════

import json
from datetime import date, timedelta
from typing import Optional
from backend.config import get_settings
from backend.services.groq_service import call_groq, build_agent_prompt
from backend.utils.peak_season import get_peak_multiplier, get_demand_signal
from backend.utils.logger import get_logger

settings = get_settings()
logger = get_logger("pricing_agent")

PRICING_SUB_PROMPT = """You are the PricingAgent for {hotel_name}.
Your job: Recommend optimal room prices for specific dates.

Given:
- Hotel's current base rates per room type
- Competitor rates (if provided)
- Current occupancy for target dates
- Upcoming local events or holidays
- Historical RevPAR trend (if available)

Output in "data" field:
{{
  "recommendations": [
    {{
      "room_type": string,
      "current_rate_lkr": number,
      "recommended_rate_lkr": number,
      "change_percent": number,
      "multiplier_applied": number,
      "reasoning": string
    }}
  ],
  "demand_signal": "low" | "medium" | "high" | "peak",
  "valid_for_dates": [string]
}}

PRICING RULES:
- Never go below hotel minimum rate.
- Apply peak multipliers automatically for Sri Lanka holidays/events.
- If occupancy > 85%: increase price 10-25% above base.
- If occupancy < 40%: decrease price 5-15% below base (but not below minimum).
- If competitor rates available: price within 5-15% of market midpoint.
- Round all prices to nearest LKR 500."""


class PricingAgent:
    """Dynamic pricing agent with peak season awareness."""

    agent_name = "pricing_agent"

    async def run(self, task: str, hotel_profile: dict, context: dict = None) -> dict:
        context = context or {}
        hotel_name = hotel_profile.get("hotel_name", "Unknown Hotel")
        city = hotel_profile.get("city", "")
        rooms = hotel_profile.get("rooms", [])
        occupancy_data = hotel_profile.get("current_occupancy", {})
        occupancy_rate = occupancy_data.get("occupancy_rate", 50.0)

        # Determine target dates
        target_dates = context.get("target_dates", [])
        if not target_dates:
            today = date.today()
            target_dates = [(today + timedelta(days=i)).isoformat() for i in range(7)]

        # Get peak multiplier for first target date
        first_date = date.fromisoformat(target_dates[0]) if target_dates else date.today()
        multiplier, events = get_peak_multiplier(first_date, city)
        demand = get_demand_signal(occupancy_rate, multiplier)

        # Build context for LLM
        competitor_rates = context.get("competitor_rates", [])
        user_message = (
            f"Task: {task}\n"
            f"Target dates: {', '.join(target_dates[:7])}\n"
            f"Current occupancy: {occupancy_rate}%\n"
            f"Peak multiplier: {multiplier}x (events: {', '.join(events) if events else 'none'})\n"
            f"Demand signal: {demand}\n"
            f"Room types: {json.dumps(rooms)}\n"
        )
        if competitor_rates:
            user_message += f"Competitor rates: {json.dumps(competitor_rates)}\n"

        sub_prompt = PRICING_SUB_PROMPT.format(hotel_name=hotel_name)
        system_prompt = build_agent_prompt(settings.BASE_SYSTEM_PROMPT, sub_prompt, hotel_profile)

        try:
            result = await call_groq(system_prompt, user_message)
            result.setdefault("agent_used", self.agent_name)
            result.setdefault("confidence", 0.8)
            result.setdefault("escalate_to_human", False)
            logger.info(f"Pricing recommendations generated for {hotel_name}")
            return result
        except Exception as e:
            logger.error(f"PricingAgent error for {hotel_name}: {e}")
            return self._fallback_response(hotel_name, rooms, multiplier, demand, target_dates, str(e))

    def _fallback_response(self, hotel_name, rooms, multiplier, demand, dates, error):
        """Generate rule-based fallback pricing when LLM is unavailable."""
        recommendations = []
        for room in rooms:
            base = room.get("base_rate", 10000)
            min_rate = room.get("min_rate", base)
            recommended = int(base * multiplier)
            recommended = max(recommended, min_rate)
            recommended = round(recommended / 500) * 500  # Round to nearest 500
            change_pct = round((recommended - base) / base * 100, 1)
            recommendations.append({
                "room_type": room.get("type", "Standard"),
                "current_rate_lkr": base,
                "recommended_rate_lkr": recommended,
                "change_percent": change_pct,
                "multiplier_applied": multiplier,
                "reasoning": f"Rule-based: {multiplier}x multiplier applied (LLM unavailable: {error})",
            })
        return {
            "agent_used": self.agent_name,
            "action_taken": "fallback_pricing_generated",
            "output": f"Rule-based pricing for {hotel_name} (LLM unavailable). {len(recommendations)} room types priced.",
            "confidence": 0.5,
            "escalate_to_human": True,
            "escalation_reason": f"LLM unavailable, using rule-based pricing: {error}",
            "follow_up_suggested": "Review fallback pricing recommendations manually",
            "data": {"recommendations": recommendations, "demand_signal": demand, "valid_for_dates": dates[:7]},
        }
