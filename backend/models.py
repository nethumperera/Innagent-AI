# ════════════════════════════════════════════════════════════════
# InnAgent AI — Pydantic Models
# ════════════════════════════════════════════════════════════════

from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime, date
from enum import Enum


# ── Enums ─────────────────────────────────────────────────────

class AgentType(str, Enum):
    PRICING = "pricing_agent"
    GUEST_BOT = "guest_bot"
    REVENUE = "revenue_agent"
    REVIEW = "review_agent"
    OPERATIONS = "operations_agent"
    ORCHESTRATOR = "orchestrator"


class BookingStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CHECKED_IN = "checked_in"
    CHECKED_OUT = "checked_out"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"


class DemandSignal(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    PEAK = "peak"


class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Sentiment(str, Enum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    MIXED = "mixed"


class Language(str, Enum):
    ENGLISH = "english"
    SINHALA = "sinhala"
    TAMIL = "tamil"


# ── Agent Models ──────────────────────────────────────────────

class AgentRequest(BaseModel):
    task: str = Field(..., description="Task description for the agent")
    hotel_id: Optional[str] = Field(None, description="Target hotel UUID")
    agent_type: Optional[AgentType] = Field(None, description="Force specific agent")
    context: dict = Field(default_factory=dict, description="Additional context data")


class AgentResponse(BaseModel):
    agent_used: str
    action_taken: str
    output: str
    confidence: float = Field(ge=0.0, le=1.0)
    escalate_to_human: bool = False
    escalation_reason: Optional[str] = None
    follow_up_suggested: Optional[str] = None
    data: Optional[Any] = None


# ── Pricing Models ────────────────────────────────────────────

class PricingRecommendation(BaseModel):
    room_type: str
    current_rate_lkr: int
    recommended_rate_lkr: int
    change_percent: float
    multiplier_applied: float = 1.0
    reasoning: str


class PricingData(BaseModel):
    recommendations: List[PricingRecommendation]
    demand_signal: DemandSignal
    valid_for_dates: List[str]


# ── Guest Bot Models ─────────────────────────────────────────

class GuestBotData(BaseModel):
    reply_text: str
    language_detected: Language
    intent_detected: str
    upsell_offered: bool = False
    upsell_details: Optional[str] = None


# ── Revenue Models ────────────────────────────────────────────

class BenchmarkStatus(BaseModel):
    occupancy: str  # "above" | "below" | "on_target"
    revpar: str


class RevenueData(BaseModel):
    occupancy_rate: float
    adr_lkr: int
    revpar_lkr: int
    direct_booking_pct: float
    top_issue: str
    top_opportunity: str
    trend: str  # "improving" | "stable" | "declining"
    benchmark_vs_target: BenchmarkStatus


# ── Review Models ─────────────────────────────────────────────

class ReviewData(BaseModel):
    platform: str
    original_review: str
    star_rating: int
    sentiment: Sentiment
    issues_mentioned: List[str]
    response_draft: str
    urgency: str


# ── Operations Models ─────────────────────────────────────────

class TaskItem(BaseModel):
    task_id: str
    type: str
    room: str
    priority: Priority
    assigned_to: str
    due_by: str
    status: str
    notes: str


class OperationsData(BaseModel):
    task_list: List[TaskItem]
    overdue_count: int
    urgent_count: int
    staff_message_sinhala: str


# ── Hotel Models ──────────────────────────────────────────────

class HotelCreate(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    district: Optional[str] = None
    province: Optional[str] = None
    star_rating: Optional[int] = None
    total_rooms: int = 0
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    whatsapp_number: Optional[str] = None
    manager_whatsapp: Optional[str] = None
    minimum_rate_lkr: int = 5000
    amenities: List[str] = []


class HotelUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    star_rating: Optional[int] = None
    total_rooms: Optional[int] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    whatsapp_number: Optional[str] = None
    manager_whatsapp: Optional[str] = None
    minimum_rate_lkr: Optional[int] = None
    amenities: Optional[List[str]] = None
    is_active: Optional[bool] = None


class HotelProfile(BaseModel):
    id: str
    name: str
    slug: str
    description: Optional[str] = None
    city: Optional[str] = None
    district: Optional[str] = None
    star_rating: Optional[int] = None
    total_rooms: int = 0
    minimum_rate_lkr: int = 5000
    amenities: List[str] = []
    rooms: List[dict] = []


# ── Dashboard Models ──────────────────────────────────────────

class KPIMetrics(BaseModel):
    occupancy_rate: float = 0.0
    adr_lkr: int = 0
    revpar_lkr: int = 0
    open_tickets: int = 0


class DashboardSummary(BaseModel):
    hotel_id: str
    hotel_name: str
    kpis: KPIMetrics
    occupancy_trend: List[dict] = []
    revenue_by_room: List[dict] = []
    recent_activity: List[dict] = []


# ── WhatsApp Models ───────────────────────────────────────────

class WhatsAppMessage(BaseModel):
    from_number: str
    body: str
    timestamp: Optional[str] = None
    message_sid: Optional[str] = None


# ── Review Action Models ─────────────────────────────────────

class ReviewApproval(BaseModel):
    review_id: str
    action: str = Field(..., pattern="^(approve|reject|edit)$")
    edited_response: Optional[str] = None
    approved_by: str = "manager"
