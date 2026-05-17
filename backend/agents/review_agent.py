# ════════════════════════════════════════════════════════════════
# InnAgent AI — Review Agent
# Review monitoring and response draft generation
# ════════════════════════════════════════════════════════════════

import json
from backend.config import get_settings
from backend.services.groq_service import call_groq, build_agent_prompt
from backend.utils.logger import get_logger

settings = get_settings()
logger = get_logger("review_agent")

REVIEW_SUB_PROMPT = """You are the ReviewAgent for {hotel_name}.
Your job: Draft professional responses to guest reviews.

Output in "data" field:
{{
  "platform": string,
  "original_review": string,
  "star_rating": number,
  "sentiment": "positive" | "neutral" | "negative" | "mixed",
  "issues_mentioned": [string],
  "response_draft": string,
  "urgency": "low" | "medium" | "high" | "critical"
}}

RESPONSE RULES:
- Positive reviews (4-5 stars): Thank guest, highlight specific detail they mentioned, invite return. 3-4 sentences max.
- Negative reviews (1-3 stars): Acknowledge issue, apologize sincerely, explain action taken or being taken, invite direct contact. Never be defensive.
- Mention a specific staff name or amenity from the review to show it is personal.
- End with: hotel name + "Managed by Co Host Ceylon".
- Flag critical = health/safety/legal/discrimination complaint. Escalate immediately.
- All drafts await human approval before posting (escalate_to_human = true for posting)."""


class ReviewAgent:
    """Review monitoring and response drafting agent."""

    agent_name = "review_agent"

    async def run(self, task: str, hotel_profile: dict, context: dict = None) -> dict:
        context = context or {}
        hotel_name = hotel_profile.get("hotel_name", "Unknown Hotel")

        review_text = context.get("review_text", "")
        star_rating = context.get("star_rating", 0)
        platform = context.get("platform", "unknown")
        reviewer_name = context.get("reviewer_name", "Guest")

        user_message = (
            f"Task: {task}\n"
            f"Platform: {platform}\n"
            f"Reviewer: {reviewer_name}\n"
            f"Star Rating: {star_rating}/5\n"
            f"Review:\n\"{review_text}\"\n"
        )

        sub_prompt = REVIEW_SUB_PROMPT.format(hotel_name=hotel_name)
        system_prompt = build_agent_prompt(settings.BASE_SYSTEM_PROMPT, sub_prompt, hotel_profile)

        try:
            result = await call_groq(system_prompt, user_message, temperature=0.4)
            result.setdefault("agent_used", self.agent_name)
            result.setdefault("confidence", 0.8)
            # Always require human approval before posting
            result["escalate_to_human"] = True
            result.setdefault("escalation_reason", "Review response draft requires human approval before posting")

            # Ensure sign-off
            if result.get("data") and result["data"].get("response_draft"):
                draft = result["data"]["response_draft"]
                if "Co Host Ceylon" not in draft:
                    result["data"]["response_draft"] = draft + f"\n\n{hotel_name}\nManaged by Co Host Ceylon"

            logger.info(f"Review response drafted for {hotel_name} ({star_rating}★ on {platform})")
            return result

        except Exception as e:
            logger.error(f"ReviewAgent error for {hotel_name}: {e}")
            return self._fallback_response(hotel_name, platform, review_text, star_rating, reviewer_name, str(e))

    def _fallback_response(self, hotel_name, platform, review_text, rating, reviewer, error):
        """Generate a template response when LLM is unavailable."""
        sentiment = "positive" if rating >= 4 else ("neutral" if rating == 3 else "negative")
        urgency = "low" if rating >= 4 else ("medium" if rating == 3 else "high")

        if rating >= 4:
            draft = (
                f"Dear {reviewer}, thank you so much for your wonderful review! "
                f"We're delighted to hear you enjoyed your stay at {hotel_name}. "
                f"Your kind words mean a lot to our team. We look forward to welcoming you back soon!\n\n"
                f"{hotel_name}\nManaged by Co Host Ceylon"
            )
        else:
            draft = (
                f"Dear {reviewer}, thank you for sharing your feedback about your stay at {hotel_name}. "
                f"We sincerely apologize for any inconvenience you experienced. "
                f"Your concerns have been escalated to our management team for immediate review. "
                f"We would appreciate the opportunity to discuss this further — please contact us directly.\n\n"
                f"{hotel_name}\nManaged by Co Host Ceylon"
            )

        return {
            "agent_used": self.agent_name,
            "action_taken": "template_response_drafted",
            "output": f"Template review response drafted for {reviewer}'s {rating}★ review on {platform}",
            "confidence": 0.4,
            "escalate_to_human": True,
            "escalation_reason": f"Template response used (LLM unavailable: {error}). Please personalize before posting.",
            "follow_up_suggested": "Edit the response draft to include specific details from the review",
            "data": {
                "platform": platform,
                "original_review": review_text,
                "star_rating": rating,
                "sentiment": sentiment,
                "issues_mentioned": [],
                "response_draft": draft,
                "urgency": urgency,
            },
        }
