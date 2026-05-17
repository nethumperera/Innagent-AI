# ════════════════════════════════════════════════════════════════
# InnAgent AI — WhatsApp Webhook Router
# POST /webhook/whatsapp — Twilio webhook handler
# ════════════════════════════════════════════════════════════════

from fastapi import APIRouter, Request, BackgroundTasks, Response
from backend.database import get_hotel_by_whatsapp, save_conversation
from backend.agents.orchestrator import run_orchestrator
from backend.services.twilio_service import send_whatsapp_message, send_manager_alert, format_twiml_response
from backend.utils.language_detector import detect_language
from backend.utils.logger import get_logger

router = APIRouter(prefix="/webhook", tags=["Webhook"])
logger = get_logger("webhook_router")


async def _process_whatsapp_message(
    sender_phone: str,
    message_body: str,
    hotel: dict,
    message_sid: str,
):
    """Background task to process WhatsApp message with agent."""
    hotel_id = hotel["id"]
    hotel_name = hotel["name"]
    language = detect_language(message_body)

    # Save inbound message
    try:
        save_conversation({
            "hotel_id": hotel_id,
            "guest_phone": sender_phone,
            "direction": "inbound",
            "channel": "whatsapp",
            "message_body": message_body,
            "language": language,
            "twilio_message_sid": message_sid,
        })
    except Exception as e:
        logger.error(f"Failed to save inbound conversation: {e}")

    # Run GuestBot agent
    try:
        result = await run_orchestrator(
            task="guest_message",
            hotel_id=hotel_id,
            agent_type="guest_bot",
            context={
                "guest_message": message_body,
                "guest_phone": sender_phone,
                "language": language,
            },
        )

        # Extract reply text
        reply_text = ""
        data = result.get("data", {})
        if isinstance(data, dict):
            reply_text = data.get("reply_text", "")
        if not reply_text:
            reply_text = result.get("output", "Thank you for your message. A team member will assist you shortly.")

        # Send reply via Twilio
        send_result = await send_whatsapp_message(sender_phone, reply_text)

        # Save outbound message
        try:
            save_conversation({
                "hotel_id": hotel_id,
                "guest_phone": sender_phone,
                "direction": "outbound",
                "channel": "whatsapp",
                "message_body": reply_text,
                "language": language,
                "agent_used": result.get("agent_used", "guest_bot"),
                "intent": data.get("intent_detected", ""),
                "escalated": result.get("escalate_to_human", False),
                "escalation_reason": result.get("escalation_reason"),
                "twilio_message_sid": send_result.get("message_sid"),
            })
        except Exception as e:
            logger.error(f"Failed to save outbound conversation: {e}")

        # Send manager alert if escalated
        if result.get("escalate_to_human"):
            manager_phone = hotel.get("manager_whatsapp")
            if manager_phone:
                alert_msg = (
                    f"Guest ({sender_phone}) requires attention.\n"
                    f"Reason: {result.get('escalation_reason', 'Unknown')}\n"
                    f"Message: {message_body[:200]}"
                )
                await send_manager_alert(manager_phone, hotel_name, alert_msg)

        logger.info(f"WhatsApp processed for {hotel_name}: {sender_phone}")

    except Exception as e:
        logger.error(f"Failed to process WhatsApp message: {e}", exc_info=True)
        # Send fallback reply
        try:
            fallback = f"Thank you for contacting {hotel_name}. Our team will get back to you shortly.\n\nManaged by Co Host Ceylon | Powered by InnAgent AI"
            await send_whatsapp_message(sender_phone, fallback)
        except Exception:
            pass


@router.post("/whatsapp")
async def whatsapp_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    Twilio WhatsApp webhook endpoint.
    Must respond within 5 seconds — agent processing runs in background.
    """
    try:
        form_data = await request.form()
        sender_phone = form_data.get("From", "")
        message_body = form_data.get("Body", "")
        message_sid = form_data.get("MessageSid", "")

        logger.info(f"WhatsApp received from {sender_phone}: {message_body[:100]}")

        if not sender_phone or not message_body:
            return Response(
                content=format_twiml_response("Invalid message received."),
                media_type="application/xml",
            )

        # Strip whatsapp: prefix for hotel lookup
        clean_phone = sender_phone.replace("whatsapp:", "")

        # Look up hotel by WhatsApp number mapping
        # In production, you'd map guest phone to hotel based on the Twilio number they messaged
        # For prototype, we find any active hotel
        hotel = None
        try:
            from backend.database import get_all_hotels
            hotels = get_all_hotels(active_only=True)
            if hotels:
                hotel = hotels[0]  # Default to first active hotel for prototype
        except Exception as e:
            logger.error(f"Hotel lookup failed: {e}")

        if not hotel:
            return Response(
                content=format_twiml_response(
                    "Thank you for your message. Please contact us directly at our hotel number."
                ),
                media_type="application/xml",
            )

        # Process in background to respond within 5 seconds
        background_tasks.add_task(
            _process_whatsapp_message,
            sender_phone, message_body, hotel, message_sid,
        )

        # Immediate acknowledgment
        ack_text = "Thank you for your message! We're preparing a response for you."
        return Response(
            content=format_twiml_response(ack_text),
            media_type="application/xml",
        )

    except Exception as e:
        logger.error(f"WhatsApp webhook error: {e}", exc_info=True)
        return Response(
            content=format_twiml_response("We received your message. A team member will assist you shortly."),
            media_type="application/xml",
        )
