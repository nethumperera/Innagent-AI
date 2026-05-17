# ════════════════════════════════════════════════════════════════
# InnAgent AI — Groq API Service
# Wrapper for Groq LLM calls with token budget enforcement
# ════════════════════════════════════════════════════════════════

import json
import time
from typing import Optional
from groq import Groq
from backend.config import get_settings
from backend.utils.logger import get_logger

settings = get_settings()
logger = get_logger("groq_service")

_groq_client: Optional[Groq] = None


def get_groq_client() -> Groq:
    """Get or create Groq client singleton."""
    global _groq_client
    if _groq_client is None:
        if not settings.GROQ_API_KEY:
            raise ConnectionError("GROQ_API_KEY not configured.")
        _groq_client = Groq(api_key=settings.GROQ_API_KEY)
    return _groq_client


def _truncate_to_token_budget(text: str, max_chars: int = 3200) -> str:
    """Rough truncation to stay within token budget (1 token ≈ 4 chars)."""
    if len(text) <= max_chars:
        return text
    truncated = text[:max_chars]
    logger.warning(f"Input truncated from {len(text)} to {max_chars} chars for token budget")
    return truncated + "\n\n[Content truncated to fit token budget]"


async def call_groq(
    system_prompt: str,
    user_message: str,
    temperature: float = 0.3,
    max_output_tokens: Optional[int] = None,
) -> dict:
    """
    Call Groq API with system prompt and user message.
    Returns parsed JSON response or error dict.
    """
    client = get_groq_client()
    max_tokens = max_output_tokens or settings.GROQ_MAX_OUTPUT_TOKENS

    # Truncate inputs to stay within budget
    system_prompt = _truncate_to_token_budget(system_prompt, max_chars=2400)
    user_message = _truncate_to_token_budget(user_message, max_chars=800)

    start_time = time.time()

    try:
        response = client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
            response_format={"type": "json_object"},
        )

        elapsed_ms = int((time.time() - start_time) * 1000)
        content = response.choices[0].message.content
        tokens_used = response.usage.total_tokens if response.usage else 0

        logger.info(f"Groq call completed in {elapsed_ms}ms, tokens: {tokens_used}")

        # Parse JSON response
        try:
            parsed = json.loads(content)
            parsed["_meta"] = {
                "execution_time_ms": elapsed_ms,
                "tokens_used": tokens_used,
                "model": settings.GROQ_MODEL,
            }
            return parsed
        except json.JSONDecodeError:
            logger.error(f"Failed to parse Groq response as JSON: {content[:200]}")
            return {
                "agent_used": "unknown",
                "action_taken": "llm_response_parse_error",
                "output": content,
                "confidence": 0.3,
                "escalate_to_human": True,
                "escalation_reason": "LLM response was not valid JSON",
                "follow_up_suggested": None,
                "data": None,
                "_meta": {"execution_time_ms": elapsed_ms, "tokens_used": tokens_used},
            }

    except Exception as e:
        elapsed_ms = int((time.time() - start_time) * 1000)
        logger.error(f"Groq API error: {e}", exc_info=True)
        return {
            "agent_used": "unknown",
            "action_taken": "llm_api_error",
            "output": f"LLM service error: {str(e)}",
            "confidence": 0.0,
            "escalate_to_human": True,
            "escalation_reason": f"Groq API error: {str(e)}",
            "follow_up_suggested": "Retry the request or check API key",
            "data": None,
            "_meta": {"execution_time_ms": elapsed_ms, "tokens_used": 0, "error": str(e)},
        }


def build_agent_prompt(base_prompt: str, sub_prompt: str, hotel_profile: dict) -> str:
    """Build complete system prompt with base + hotel profile + agent sub-prompt."""
    hotel_context = (
        f"\n\nCURRENT HOTEL PROFILE:\n"
        f"- Name: {hotel_profile.get('hotel_name', 'Unknown')}\n"
        f"- City: {hotel_profile.get('city', 'Unknown')}\n"
        f"- Star Rating: {hotel_profile.get('star_rating', 'N/A')}\n"
        f"- Total Rooms: {hotel_profile.get('total_rooms', 0)}\n"
        f"- Min Rate: LKR {hotel_profile.get('minimum_rate_lkr', 0):,}\n"
        f"- Rooms: {json.dumps(hotel_profile.get('rooms', []))}\n"
        f"- Current Occupancy: {json.dumps(hotel_profile.get('current_occupancy', {}))}\n"
    )
    return base_prompt + hotel_context + "\n\n" + sub_prompt
