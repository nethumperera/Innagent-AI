# ════════════════════════════════════════════════════════════════
# InnAgent AI — Operations Agent
# Housekeeping tasks and maintenance ticket management
# ════════════════════════════════════════════════════════════════

import json
from datetime import datetime, timedelta
from backend.config import get_settings
from backend.services.groq_service import call_groq, build_agent_prompt
from backend.utils.logger import get_logger

settings = get_settings()
logger = get_logger("operations_agent")

OPS_SUB_PROMPT = """You are the OperationsAgent for {hotel_name}.
Your job: Manage housekeeping tasks and maintenance tickets.

Output in "data" field:
{{
  "task_list": [
    {{
      "task_id": string,
      "type": "housekeeping" | "maintenance" | "inspection",
      "room": string,
      "priority": "low" | "medium" | "high" | "urgent",
      "assigned_to": string,
      "due_by": string,
      "status": "pending" | "in_progress" | "completed" | "overdue",
      "notes": string
    }}
  ],
  "overdue_count": number,
  "urgent_count": number,
  "staff_message_sinhala": string
}}

RULES:
- Maintenance older than 24h = overdue, escalate to manager.
- Urgent = guest-impacting (no hot water, broken A/C, safety hazard).
- Staff WhatsApp message must be in Sinhala Unicode.
- Prioritize: urgent > checkout rooms > occupied rooms > vacant rooms."""


class OperationsAgent:
    """Housekeeping and maintenance operations agent."""

    agent_name = "operations_agent"

    async def run(self, task: str, hotel_profile: dict, context: dict = None) -> dict:
        context = context or {}
        hotel_name = hotel_profile.get("hotel_name", "Unknown Hotel")
        total_rooms = hotel_profile.get("total_rooms", 0)

        existing_tickets = context.get("existing_tickets", [])
        checkouts_today = context.get("checkouts_today", [])
        checkins_today = context.get("checkins_today", [])

        user_message = (
            f"Task: {task}\n"
            f"Hotel: {hotel_name} ({total_rooms} rooms)\n"
            f"Today's checkouts: {json.dumps(checkouts_today) if checkouts_today else 'None'}\n"
            f"Today's check-ins: {json.dumps(checkins_today) if checkins_today else 'None'}\n"
            f"Open maintenance tickets: {json.dumps(existing_tickets) if existing_tickets else 'None'}\n"
        )

        sub_prompt = OPS_SUB_PROMPT.format(hotel_name=hotel_name)
        system_prompt = build_agent_prompt(settings.BASE_SYSTEM_PROMPT, sub_prompt, hotel_profile)

        try:
            result = await call_groq(system_prompt, user_message)
            result.setdefault("agent_used", self.agent_name)
            result.setdefault("confidence", 0.8)

            # Check for overdue tickets and escalate
            data = result.get("data", {})
            overdue = data.get("overdue_count", 0)
            urgent = data.get("urgent_count", 0)
            if overdue > 0 or urgent > 0:
                result["escalate_to_human"] = True
                result["escalation_reason"] = f"{overdue} overdue, {urgent} urgent tasks require attention"

            logger.info(f"Operations tasks generated for {hotel_name}")
            return result

        except Exception as e:
            logger.error(f"OperationsAgent error for {hotel_name}: {e}")
            return self._fallback_response(hotel_name, checkouts_today, existing_tickets, str(e))

    def _fallback_response(self, hotel_name, checkouts, tickets, error):
        """Generate basic task list when LLM is unavailable."""
        now = datetime.utcnow()
        task_list = []

        # Create housekeeping tasks for checkout rooms
        for i, checkout in enumerate(checkouts or []):
            room = checkout.get("room", f"Room {i + 1}")
            task_list.append({
                "task_id": f"HK-{now.strftime('%Y%m%d')}-{i + 1:03d}",
                "type": "housekeeping",
                "room": room,
                "priority": "high",
                "assigned_to": "Housekeeping Team",
                "due_by": (now + timedelta(hours=3)).isoformat(),
                "status": "pending",
                "notes": f"Checkout cleaning for {room}",
            })

        # Check existing tickets for overdue
        overdue_count = 0
        urgent_count = 0
        for ticket in (tickets or []):
            created = ticket.get("created_at", "")
            if created:
                try:
                    created_dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
                    if (now - created_dt.replace(tzinfo=None)).total_seconds() > 86400:
                        overdue_count += 1
                except (ValueError, TypeError):
                    pass
            if ticket.get("priority") == "urgent":
                urgent_count += 1

        sinhala_msg = (
            f"🏨 {hotel_name} - අද දිනයේ කාර්ය ලැයිස්තුව:\n"
            f"• පිරිසිදු කිරීමේ කාර්යයන්: {len(task_list)}\n"
            f"• කල් ඉකුත් වූ ටිකට්: {overdue_count}\n"
            f"• හදිසි: {urgent_count}\n"
            f"කරුණාකර ප්‍රමුඛතා පදනම මත සම්පූර්ණ කරන්න."
        )

        return {
            "agent_used": self.agent_name,
            "action_taken": "fallback_task_list_generated",
            "output": f"Basic task list for {hotel_name}: {len(task_list)} tasks",
            "confidence": 0.5,
            "escalate_to_human": overdue_count > 0 or urgent_count > 0,
            "escalation_reason": f"{overdue_count} overdue, {urgent_count} urgent" if (overdue_count + urgent_count) > 0 else None,
            "follow_up_suggested": "Review and assign tasks to specific staff members",
            "data": {
                "task_list": task_list,
                "overdue_count": overdue_count,
                "urgent_count": urgent_count,
                "staff_message_sinhala": sinhala_msg,
            },
        }
