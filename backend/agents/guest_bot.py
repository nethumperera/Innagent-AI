# ════════════════════════════════════════════════════════════════
# InnAgent AI — Guest Bot
# Multilingual guest communication agent
# ════════════════════════════════════════════════════════════════

import json
from backend.config import get_settings
from backend.services.groq_service import call_groq, build_agent_prompt
from backend.utils.language_detector import detect_language
from backend.utils.logger import get_logger

settings = get_settings()
logger = get_logger("guest_bot")

GUEST_BOT_SUB_PROMPT = """You are the GuestBot for {hotel_name}.
Your job: Draft or send replies to guest inquiries and messages.

Tone: Warm, professional, helpful. Never robotic. Never rude.
Language: Match the guest's language exactly.
- English: Formal but friendly hotel style.
- Sinhala: Proper Unicode Sinhala script. Polite formal register.
- Tamil: Proper Unicode Tamil script. Polite formal register.

Output in "data" field:
{{
  "reply_text": string,
  "language_detected": "english" | "sinhala" | "tamil",
  "intent_detected": string,
  "upsell_offered": boolean,
  "upsell_details": string or null
}}

GUEST BOT RULES:
- Answer ALL questions in the guest's message. Never ignore a sub-question.
- For room availability: check hotel profile room types and state options clearly.
- For pricing: quote base rate + note "+12% VAT". Never invent special discounts.
- Upsell upgrades ONLY if: occupancy < 80% AND upgrade is available AND booking is confirmed AND context is appropriate.
- Never promise refunds > LKR 5,000 without manager approval.
- Escalate: complaints severity >= 4/5, health/safety, legal questions.
- Sign off with hotel name and "InnAgent AI | Powered by Co Host Ceylon"."""


class GuestBot:
    """Multilingual guest communication agent."""

    agent_name = "guest_bot"

    async def run(self, task: str, hotel_profile: dict, context: dict = None) -> dict:
        context = context or {}
        hotel_name = hotel_profile.get("hotel_name", "Unknown Hotel")
        guest_message = context.get("guest_message", task)
        guest_phone = context.get("guest_phone", "unknown")

        # Detect language
        language = detect_language(guest_message)
        occupancy = hotel_profile.get("current_occupancy", {}).get("occupancy_rate", 50.0)

        user_message = (
            f"Guest message (from {guest_phone}):\n\"{guest_message}\"\n\n"
            f"Detected language: {language}\n"
            f"Current occupancy: {occupancy}%\n"
            f"Available room types: {json.dumps(hotel_profile.get('rooms', []))}\n"
        )

        # Add booking context if available
        booking_info = context.get("booking_info")
        if booking_info:
            user_message += f"Guest booking: {json.dumps(booking_info)}\n"

        sub_prompt = GUEST_BOT_SUB_PROMPT.format(hotel_name=hotel_name)
        system_prompt = build_agent_prompt(settings.BASE_SYSTEM_PROMPT, sub_prompt, hotel_profile)

        try:
            result = await call_groq(system_prompt, user_message, temperature=0.5)
            result.setdefault("agent_used", self.agent_name)
            result.setdefault("confidence", 0.85)
            result.setdefault("escalate_to_human", False)

            # Ensure sign-off is in the reply
            if result.get("data") and result["data"].get("reply_text"):
                reply = result["data"]["reply_text"]
                sign_off = f"\n\n{hotel_name}\nManaged by Co Host Ceylon | Powered by InnAgent AI"
                if "Co Host Ceylon" not in reply:
                    result["data"]["reply_text"] = reply + sign_off

            logger.info(f"GuestBot reply generated for {hotel_name}, lang={language}")
            return result

        except Exception as e:
            logger.error(f"GuestBot error for {hotel_name}: {e}")
            return self._fallback_response(hotel_name, language, guest_message, str(e))

    def _fallback_response(self, hotel_name, language, message, error):
        """Generate a polite holding reply when LLM is unavailable."""
        replies = {
            "english": (
                f"Thank you for reaching out to {hotel_name}! We've received your message "
                f"and a team member will get back to you shortly.\n\n"
                f"{hotel_name}\nManaged by Co Host Ceylon | Powered by InnAgent AI"
            ),
            "sinhala": (
                f"{hotel_name} වෙත සම්බන්ධ වීමට ස්තූතියි! ඔබගේ පණිවිඩය ලැබුණා. "
                f"කණ්ඩායම් සාමාජිකයෙක් ඉක්මනින් ඔබව සම්බන්ධ කර ගනී.\n\n"
                f"{hotel_name}\nManaged by Co Host Ceylon | Powered by InnAgent AI"
            ),
            "tamil": (
                f"{hotel_name} ஐ தொடர்பு கொண்டதற்கு நன்றி! உங்கள் செய்தி பெறப்பட்டது. "
                f"குழு உறுப்பினர் விரைவில் உங்களைத் தொடர்புகொள்வார்.\n\n"
                f"{hotel_name}\nManaged by Co Host Ceylon | Powered by InnAgent AI"
            ),
        }
        reply = replies.get(language, replies["english"])
        return {
            "agent_used": self.agent_name,
            "action_taken": "fallback_reply_sent",
            "output": f"Fallback reply sent in {language} (LLM unavailable)",
            "confidence": 0.4,
            "escalate_to_human": True,
            "escalation_reason": f"LLM unavailable: {error}. Holding reply sent.",
            "follow_up_suggested": "Review guest message and send a detailed reply",
            "data": {
                "reply_text": reply,
                "language_detected": language,
                "intent_detected": "general_inquiry",
                "upsell_offered": False,
                "upsell_details": None,
            },
        }
