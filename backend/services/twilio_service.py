# ════════════════════════════════════════════════════════════════
# InnAgent AI — Twilio WhatsApp Service
# Send/receive WhatsApp messages via Twilio API
# ════════════════════════════════════════════════════════════════

from twilio.rest import Client
from typing import Optional
from backend.config import get_settings
from backend.utils.logger import get_logger

settings = get_settings()
logger = get_logger("twilio_service")

_twilio_client: Optional[Client] = None


def get_twilio_client() -> Client:
    """Get or create Twilio client singleton."""
    global _twilio_client
    if _twilio_client is None:
        if not settings.TWILIO_ACCOUNT_SID or not settings.TWILIO_AUTH_TOKEN:
            raise ConnectionError("Twilio credentials not configured.")
        _twilio_client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    return _twilio_client


async def send_whatsapp_message(to_number: str, message: str) -> dict:
    """
    Send a WhatsApp message via Twilio.
    to_number should be in format: whatsapp:+94XXXXXXXXX
    """
    try:
        client = get_twilio_client()

        # Ensure number has whatsapp: prefix
        if not to_number.startswith("whatsapp:"):
            to_number = f"whatsapp:{to_number}"

        msg = client.messages.create(
            body=message,
            from_=settings.TWILIO_WHATSAPP_FROM,
            to=to_number,
        )

        logger.info(f"WhatsApp sent to {to_number}, SID: {msg.sid}")
        return {
            "success": True,
            "message_sid": msg.sid,
            "status": msg.status,
        }

    except Exception as e:
        logger.error(f"Failed to send WhatsApp to {to_number}: {e}")
        return {
            "success": False,
            "error": str(e),
        }


async def send_manager_alert(manager_number: str, hotel_name: str, alert_message: str) -> dict:
    """Send an escalation alert to the hotel manager's WhatsApp."""
    full_message = (
        f"🚨 *InnAgent AI Alert — {hotel_name}*\n\n"
        f"{alert_message}\n\n"
        f"_Please review and take action in the InnAgent AI dashboard._\n"
        f"_Managed by Co Host Ceylon_"
    )
    return await send_whatsapp_message(manager_number, full_message)


def format_twiml_response(reply_text: str) -> str:
    """Format a TwiML response for Twilio webhook."""
    # Escape XML special characters
    escaped = (
        reply_text
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )
    return (
        '<?xml version="1.0" encoding="UTF-8"?>'
        f"<Response><Message>{escaped}</Message></Response>"
    )
