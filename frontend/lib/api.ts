// ════════════════════════════════════════════════════════════════
// InnAgent AI — Axios API Client
// ════════════════════════════════════════════════════════════════

import axios from "axios";
import type {
  Hotel, DashboardSummary, MetricsResponse,
  AgentRequest, AgentResponse, Review, MaintenanceTicket, Conversation, ConversationItem,
} from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const api = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
  headers: { "Content-Type": "application/json" },
});

// ── Hotels ───────────────────────────────────────────────────

export async function fetchHotels(): Promise<Hotel[]> {
  const res = await api.get("/hotels/");
  return res.data.hotels;
}

export async function fetchHotel(hotelId: string): Promise<Hotel> {
  const res = await api.get(`/hotels/${hotelId}`);
  return res.data;
}

// ── Dashboard ────────────────────────────────────────────────

export async function fetchDashboardSummary(hotelId: string): Promise<DashboardSummary> {
  const res = await api.get(`/dashboard/summary/${hotelId}`);
  return res.data;
}

export async function fetchMetrics(hotelId: string, days = 7): Promise<MetricsResponse> {
  const res = await api.get(`/dashboard/metrics/${hotelId}`, { params: { days } });
  return res.data;
}

export async function fetchActivity(hotelId?: string, limit = 10) {
  const res = await api.get("/dashboard/activity", { params: { hotel_id: hotelId, limit } });
  return res.data.activity;
}

export async function fetchTasks(hotelId: string, status?: string): Promise<MaintenanceTicket[]> {
  const res = await api.get(`/dashboard/tasks/${hotelId}`, { params: { status } });
  return res.data.tasks;
}

// ── Agent ────────────────────────────────────────────────────

export async function runAgent(request: AgentRequest): Promise<AgentResponse> {
  const res = await api.post("/agent/run", request);
  return res.data;
}

// ── Reviews ──────────────────────────────────────────────────

export async function fetchReviews(hotelId: string, status?: string): Promise<Review[]> {
  const res = await api.get(`/reviews/${hotelId}`, { params: { status } });
  return res.data.reviews;
}

export async function reviewAction(reviewId: string, action: string, editedResponse?: string) {
  const res = await api.post("/reviews/action", {
    review_id: reviewId,
    action,
    edited_response: editedResponse,
  });
  return res.data;
}

// ── Conversations ────────────────────────────────────────────

export async function fetchConversations(hotelId: string): Promise<ConversationItem[]> {
  try {
    const res = await api.get(`/dashboard/conversations/${hotelId}`);
    return res.data.conversations || [];
  } catch {
    return [];
  }
}

export async function fetchConversationThread(hotelId: string, guestPhone: string) {
  try {
    // URL encode the phone number to handle the + sign properly
    const encodedPhone = encodeURIComponent(guestPhone);
    const res = await api.get(`/dashboard/conversations/${hotelId}/${encodedPhone}`);
    return res.data.messages || [];
  } catch {
    return [];
  }
}

export default api;
