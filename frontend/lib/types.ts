// ════════════════════════════════════════════════════════════════
// InnAgent AI — TypeScript Interfaces
// Matching Pydantic models from the backend
// ════════════════════════════════════════════════════════════════

export interface Hotel {
  id: string;
  name: string;
  slug: string;
  description?: string;
  address?: string;
  city?: string;
  district?: string;
  province?: string;
  star_rating?: number;
  total_rooms: number;
  contact_email?: string;
  contact_phone?: string;
  whatsapp_number?: string;
  minimum_rate_lkr: number;
  amenities: string[];
  is_active: boolean;
  rooms?: Room[];
  created_at: string;
  updated_at: string;
}

export interface Room {
  id: string;
  hotel_id: string;
  room_type: string;
  description?: string;
  base_rate_lkr: number;
  max_rate_lkr?: number;
  min_rate_lkr?: number;
  capacity_adults: number;
  capacity_children: number;
  total_count: number;
  bed_type?: string;
  size_sqm?: number;
}

export interface AgentRequest {
  task: string;
  hotel_id: string;
  agent_type?: string;
  context?: Record<string, unknown>;
}

export interface AgentResponse {
  agent_used: string;
  action_taken: string;
  output: string;
  confidence: number;
  escalate_to_human: boolean;
  escalation_reason?: string;
  follow_up_suggested?: string;
  data?: Record<string, unknown>;
}

export interface KPIMetrics {
  occupancy_rate: number;
  adr_lkr: number;
  revpar_lkr: number;
  open_tickets: number;
}

export interface DashboardSummary {
  hotel_id: string;
  hotel_name: string;
  kpis: KPIMetrics;
  recent_activity: AgentLog[];
}

export interface AgentLog {
  id: string;
  hotel_id: string;
  agent_name: string;
  task: string;
  confidence?: number;
  escalated: boolean;
  execution_time_ms?: number;
  created_at: string;
  output_data?: Record<string, unknown>;
}

export interface OccupancyDataPoint {
  date: string;
  occupancy: number;
}

export interface RevenueByRoom {
  room_type: string;
  revenue: number;
}

export interface PricingRecommendation {
  room_type: string;
  current_rate_lkr: number;
  recommended_rate_lkr: number;
  change_percent: number;
  multiplier_applied: number;
  reasoning: string;
}

export interface Conversation {
  id: string;
  hotel_id: string;
  guest_phone: string;
  guest_name?: string;
  direction: "inbound" | "outbound";
  channel: string;
  message_body: string;
  language: string;
  intent?: string;
  agent_used?: string;
  escalated: boolean;
  created_at: string;
}

export interface Review {
  id: string;
  hotel_id: string;
  platform: string;
  reviewer_name?: string;
  star_rating: number;
  review_text: string;
  review_date?: string;
  sentiment?: string;
  issues_mentioned: string[];
  response_draft?: string;
  response_status: string;
  urgency: string;
  created_at: string;
}

export interface MaintenanceTicket {
  id: string;
  hotel_id: string;
  task_type: string;
  room?: string;
  title: string;
  description?: string;
  priority: string;
  assigned_to?: string;
  status: string;
  due_by?: string;
  completed_at?: string;
  notes?: string;
  created_at: string;
}

export interface MetricsResponse {
  hotel_id: string;
  period_days: number;
  occupancy_trend: OccupancyDataPoint[];
  revenue_by_room: RevenueByRoom[];
  daily_metrics: DailyMetric[];
}

export interface DailyMetric {
  id: string;
  hotel_id: string;
  date: string;
  total_rooms: number;
  rooms_sold: number;
  occupancy_rate: number;
  adr_lkr: number;
  revpar_lkr: number;
  total_revenue_lkr: number;
}
