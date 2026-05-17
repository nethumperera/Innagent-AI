# ════════════════════════════════════════════════════════════════
# InnAgent AI — Database Client (Supabase)
# ════════════════════════════════════════════════════════════════

from supabase import create_client, Client
from backend.config import get_settings
from typing import Optional, List
from datetime import date, datetime, timedelta
import json

settings = get_settings()

_supabase_client: Optional[Client] = None


def get_supabase() -> Client:
    """Get or create Supabase client singleton."""
    global _supabase_client
    if _supabase_client is None:
        if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_ROLE_KEY:
            raise ConnectionError("Supabase credentials not configured. Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY.")
        _supabase_client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)
    return _supabase_client


# ── Hotel Queries ─────────────────────────────────────────────

def get_all_hotels(active_only: bool = True) -> List[dict]:
    db = get_supabase()
    query = db.table("hotels").select("*")
    if active_only:
        query = query.eq("is_active", True)
    result = query.order("name").execute()
    return result.data


def get_hotel_by_id(hotel_id: str) -> Optional[dict]:
    db = get_supabase()
    result = db.table("hotels").select("*").eq("id", hotel_id).single().execute()
    return result.data


def get_hotel_by_whatsapp(whatsapp_number: str) -> Optional[dict]:
    db = get_supabase()
    result = db.table("hotels").select("*").eq("whatsapp_number", whatsapp_number).eq("is_active", True).execute()
    return result.data[0] if result.data else None


def create_hotel(data: dict) -> dict:
    db = get_supabase()
    result = db.table("hotels").insert(data).execute()
    return result.data[0]


def update_hotel(hotel_id: str, data: dict) -> dict:
    db = get_supabase()
    result = db.table("hotels").update(data).eq("id", hotel_id).execute()
    return result.data[0] if result.data else {}


def delete_hotel(hotel_id: str) -> bool:
    db = get_supabase()
    db.table("hotels").update({"is_active": False}).eq("id", hotel_id).execute()
    return True


# ── Room Queries ──────────────────────────────────────────────

def get_rooms_by_hotel(hotel_id: str) -> List[dict]:
    db = get_supabase()
    result = db.table("rooms").select("*").eq("hotel_id", hotel_id).eq("is_active", True).execute()
    return result.data


# ── Booking Queries ───────────────────────────────────────────

def get_bookings_by_hotel(hotel_id: str, start_date: Optional[date] = None, end_date: Optional[date] = None) -> List[dict]:
    db = get_supabase()
    query = db.table("bookings").select("*").eq("hotel_id", hotel_id)
    if start_date:
        query = query.gte("check_in", start_date.isoformat())
    if end_date:
        query = query.lte("check_out", end_date.isoformat())
    result = query.order("check_in").execute()
    return result.data


def get_occupancy_for_date(hotel_id: str, target_date: date) -> dict:
    db = get_supabase()
    hotel = get_hotel_by_id(hotel_id)
    total_rooms = hotel["total_rooms"] if hotel else 0
    bookings = db.table("bookings").select("num_rooms").eq("hotel_id", hotel_id).lte("check_in", target_date.isoformat()).gte("check_out", target_date.isoformat()).in_("status", ["confirmed", "checked_in"]).execute()
    rooms_sold = sum(b.get("num_rooms", 1) for b in bookings.data)
    occupancy = (rooms_sold / total_rooms * 100) if total_rooms > 0 else 0
    return {"total_rooms": total_rooms, "rooms_sold": rooms_sold, "occupancy_rate": round(occupancy, 1)}


# ── Conversation Queries ─────────────────────────────────────

def save_conversation(data: dict) -> dict:
    db = get_supabase()
    result = db.table("guest_conversations").insert(data).execute()
    return result.data[0]


def get_conversations_by_hotel(hotel_id: str, limit: int = 50) -> List[dict]:
    db = get_supabase()
    result = db.table("guest_conversations").select("*").eq("hotel_id", hotel_id).order("created_at", desc=True).limit(limit).execute()
    return result.data


def get_conversation_thread(hotel_id: str, guest_phone: str) -> List[dict]:
    db = get_supabase()
    result = db.table("guest_conversations").select("*").eq("hotel_id", hotel_id).eq("guest_phone", guest_phone).order("created_at").execute()
    return result.data


# ── Pricing Queries ───────────────────────────────────────────

def save_pricing_recommendation(data: dict) -> dict:
    db = get_supabase()
    result = db.table("pricing_recommendations").insert(data).execute()
    return result.data[0]


def get_pricing_recommendations(hotel_id: str, status: Optional[str] = None) -> List[dict]:
    db = get_supabase()
    query = db.table("pricing_recommendations").select("*").eq("hotel_id", hotel_id)
    if status:
        query = query.eq("status", status)
    result = query.order("created_at", desc=True).limit(50).execute()
    return result.data


# ── Review Queries ────────────────────────────────────────────

def save_review(data: dict) -> dict:
    db = get_supabase()
    result = db.table("reviews").insert(data).execute()
    return result.data[0]


def get_reviews_by_hotel(hotel_id: str, status: Optional[str] = None) -> List[dict]:
    db = get_supabase()
    query = db.table("reviews").select("*").eq("hotel_id", hotel_id)
    if status:
        query = query.eq("response_status", status)
    result = query.order("created_at", desc=True).limit(50).execute()
    return result.data


def update_review(review_id: str, data: dict) -> dict:
    db = get_supabase()
    result = db.table("reviews").update(data).eq("id", review_id).execute()
    return result.data[0] if result.data else {}


# ── Maintenance Queries ───────────────────────────────────────

def save_maintenance_ticket(data: dict) -> dict:
    db = get_supabase()
    result = db.table("maintenance_tickets").insert(data).execute()
    return result.data[0]


def get_tickets_by_hotel(hotel_id: str, status: Optional[str] = None) -> List[dict]:
    db = get_supabase()
    query = db.table("maintenance_tickets").select("*").eq("hotel_id", hotel_id)
    if status:
        query = query.eq("status", status)
    result = query.order("created_at", desc=True).limit(100).execute()
    return result.data


def get_open_ticket_count(hotel_id: str) -> int:
    db = get_supabase()
    result = db.table("maintenance_tickets").select("id", count="exact").eq("hotel_id", hotel_id).in_("status", ["pending", "in_progress", "overdue"]).execute()
    return result.count or 0


# ── Agent Log Queries ─────────────────────────────────────────

def save_agent_log(data: dict) -> dict:
    db = get_supabase()
    result = db.table("agent_logs").insert(data).execute()
    return result.data[0]


def get_recent_agent_logs(hotel_id: Optional[str] = None, limit: int = 10) -> List[dict]:
    db = get_supabase()
    query = db.table("agent_logs").select("*")
    if hotel_id:
        query = query.eq("hotel_id", hotel_id)
    result = query.order("created_at", desc=True).limit(limit).execute()
    return result.data


# ── Metrics Queries ───────────────────────────────────────────

def save_daily_metric(data: dict) -> dict:
    db = get_supabase()
    result = db.table("daily_metrics").upsert(data, on_conflict="hotel_id,date").execute()
    return result.data[0]


def get_metrics_range(hotel_id: str, start_date: date, end_date: date) -> List[dict]:
    db = get_supabase()
    result = db.table("daily_metrics").select("*").eq("hotel_id", hotel_id).gte("date", start_date.isoformat()).lte("date", end_date.isoformat()).order("date").execute()
    return result.data


def get_latest_metrics(hotel_id: str) -> Optional[dict]:
    db = get_supabase()
    result = db.table("daily_metrics").select("*").eq("hotel_id", hotel_id).order("date", desc=True).limit(1).execute()
    return result.data[0] if result.data else None


# ── Hotel Profile Builder ────────────────────────────────────

def build_hotel_profile(hotel_id: str) -> dict:
    """Build a complete hotel profile dict for agent context."""
    hotel = get_hotel_by_id(hotel_id)
    if not hotel:
        return {}
    rooms = get_rooms_by_hotel(hotel_id)
    today = date.today()
    occupancy = get_occupancy_for_date(hotel_id, today)
    metrics = get_latest_metrics(hotel_id)
    return {
        "hotel_id": hotel["id"],
        "hotel_name": hotel["name"],
        "city": hotel.get("city", ""),
        "district": hotel.get("district", ""),
        "star_rating": hotel.get("star_rating"),
        "total_rooms": hotel.get("total_rooms", 0),
        "minimum_rate_lkr": hotel.get("minimum_rate_lkr", 5000),
        "amenities": hotel.get("amenities", []),
        "check_in_time": str(hotel.get("check_in_time", "14:00")),
        "check_out_time": str(hotel.get("check_out_time", "11:00")),
        "rooms": [{"type": r["room_type"], "base_rate": r["base_rate_lkr"], "min_rate": r.get("min_rate_lkr"), "max_rate": r.get("max_rate_lkr"), "count": r["total_count"]} for r in rooms],
        "current_occupancy": occupancy,
        "latest_metrics": metrics,
    }
