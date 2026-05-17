"use client";

import { useState, useEffect } from "react";
import Sidebar from "@/components/layout/Sidebar";
import Header from "@/components/layout/Header";
import MobileNav from "@/components/layout/MobileNav";
import KPICard from "@/components/dashboard/KPICard";
import OccupancyChart from "@/components/dashboard/OccupancyChart";
import RevenueChart from "@/components/dashboard/RevenueChart";
import ActivityFeed from "@/components/dashboard/ActivityFeed";
import Button from "@/components/ui/Button";
import { fetchHotels, fetchDashboardSummary, fetchMetrics, fetchActivity } from "@/lib/api";
import { formatLKR, formatPercent } from "@/lib/formatters";
import {
  Bed, DollarSign, TrendingUp, Wrench, Zap,
  MessageSquare, Star, ClipboardList,
} from "lucide-react";
import type { Hotel, AgentLog, OccupancyDataPoint, RevenueByRoom } from "@/lib/types";
import Link from "next/link";

// Demo data for when API is not connected
const DEMO_HOTELS: Hotel[] = [
  {
    id: "demo-1", name: "Kandy Heritage Villa", slug: "kandy-heritage-villa",
    city: "Kandy", district: "Kandy", star_rating: 4, total_rooms: 12,
    minimum_rate_lkr: 8000, amenities: ["WiFi", "Pool", "Restaurant", "Spa"],
    is_active: true, created_at: "2026-01-01", updated_at: "2026-05-17",
  },
  {
    id: "demo-2", name: "Galle Fort Boutique", slug: "galle-fort-boutique",
    city: "Galle", district: "Galle", star_rating: 4, total_rooms: 8,
    minimum_rate_lkr: 12000, amenities: ["WiFi", "Rooftop Bar", "Restaurant"],
    is_active: true, created_at: "2026-01-01", updated_at: "2026-05-17",
  },
];

const DEMO_OCCUPANCY: OccupancyDataPoint[] = [
  { date: "2026-05-11", occupancy: 58.3 }, { date: "2026-05-12", occupancy: 66.7 },
  { date: "2026-05-13", occupancy: 75.0 }, { date: "2026-05-14", occupancy: 83.3 },
  { date: "2026-05-15", occupancy: 75.0 }, { date: "2026-05-16", occupancy: 66.7 },
  { date: "2026-05-17", occupancy: 72.5 },
];

const DEMO_REVENUE: RevenueByRoom[] = [
  { room_type: "Standard Double", revenue: 48000 },
  { room_type: "Deluxe King", revenue: 72000 },
  { room_type: "Heritage Suite", revenue: 84000 },
  { room_type: "Family Room", revenue: 22000 },
];

const DEMO_ACTIVITY: AgentLog[] = [
  { id: "1", hotel_id: "demo-1", agent_name: "pricing_agent", task: "Daily pricing check — 4 room types optimized", confidence: 0.87, escalated: false, execution_time_ms: 1200, created_at: new Date(Date.now() - 3600000).toISOString(), output_data: {} },
  { id: "2", hotel_id: "demo-1", agent_name: "guest_bot", task: "Guest inquiry: room availability for Dec 24-27", confidence: 0.92, escalated: false, execution_time_ms: 800, created_at: new Date(Date.now() - 7200000).toISOString(), output_data: {} },
  { id: "3", hotel_id: "demo-1", agent_name: "review_agent", task: "Draft response for 4★ Booking.com review", confidence: 0.85, escalated: true, execution_time_ms: 950, created_at: new Date(Date.now() - 10800000).toISOString(), output_data: {} },
  { id: "4", hotel_id: "demo-1", agent_name: "operations_agent", task: "Generated 6 housekeeping tasks for today", confidence: 0.88, escalated: false, execution_time_ms: 1100, created_at: new Date(Date.now() - 14400000).toISOString(), output_data: {} },
  { id: "5", hotel_id: "demo-1", agent_name: "revenue_agent", task: "Weekly revenue report — RevPAR up 8.5%", confidence: 0.91, escalated: false, execution_time_ms: 700, created_at: new Date(Date.now() - 18000000).toISOString(), output_data: {} },
];

export default function DashboardPage() {
  const [hotels, setHotels] = useState<Hotel[]>(DEMO_HOTELS);
  const [selectedHotel, setSelectedHotel] = useState<Hotel>(DEMO_HOTELS[0]);
  const [darkMode, setDarkMode] = useState(false);
  const [loading, setLoading] = useState(false);
  const [occupancyData, setOccupancyData] = useState(DEMO_OCCUPANCY);
  const [revenueData, setRevenueData] = useState(DEMO_REVENUE);
  const [activity, setActivity] = useState<AgentLog[]>(DEMO_ACTIVITY);
  const [kpis, setKpis] = useState({ occupancy_rate: 72.5, adr_lkr: 18500, revpar_lkr: 13413, open_tickets: 3 });

  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
    document.documentElement.classList.toggle("dark");
  };

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      try {
        const h = await fetchHotels();
        if (h.length > 0) {
          setHotels(h);
          setSelectedHotel(h[0]);
          const summary = await fetchDashboardSummary(h[0].id);
          setKpis(summary.kpis);
          setActivity(summary.recent_activity || DEMO_ACTIVITY);
          const metrics = await fetchMetrics(h[0].id, 7);
          if (metrics.occupancy_trend.length > 0) setOccupancyData(metrics.occupancy_trend);
          if (metrics.revenue_by_room.length > 0) setRevenueData(metrics.revenue_by_room);
        }
      } catch {
        // Use demo data on API failure
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, []);

  const handleHotelChange = async (hotel: Hotel) => {
    setSelectedHotel(hotel);
    try {
      const summary = await fetchDashboardSummary(hotel.id);
      setKpis(summary.kpis);
      setActivity(summary.recent_activity || DEMO_ACTIVITY);
    } catch {
      // Keep demo data
    }
  };

  return (
    <div className="flex min-h-screen bg-background dark:bg-gray-950">
      <Sidebar />
      <div className="flex-1 lg:ml-64">
        <Header
          hotels={hotels}
          selectedHotel={selectedHotel}
          onSelectHotel={handleHotelChange}
          darkMode={darkMode}
          onToggleDarkMode={toggleDarkMode}
        />

        <main className="p-4 md:p-6 lg:p-8 pb-24 lg:pb-8 space-y-6">
          {/* Page Title */}
          <div>
            <h1 className="text-2xl font-bold text-foreground dark:text-white">
              Dashboard
            </h1>
            <p className="text-sm text-muted mt-1">
              {selectedHotel.name} — {selectedHotel.city} • {selectedHotel.total_rooms} rooms
            </p>
          </div>

          {/* KPI Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <KPICard
              title="Today's Occupancy"
              value={formatPercent(kpis.occupancy_rate)}
              icon={<Bed className="w-6 h-6" />}
              color="primary"
              trend={5.2}
              trendLabel="vs last week"
              loading={loading}
            />
            <KPICard
              title="ADR"
              value={formatLKR(kpis.adr_lkr)}
              icon={<DollarSign className="w-6 h-6" />}
              color="gold"
              trend={3.1}
              trendLabel="vs last week"
              loading={loading}
            />
            <KPICard
              title="RevPAR"
              value={formatLKR(kpis.revpar_lkr)}
              icon={<TrendingUp className="w-6 h-6" />}
              color="emerald"
              trend={8.5}
              trendLabel="vs last week"
              loading={loading}
            />
            <KPICard
              title="Open Tickets"
              value={String(kpis.open_tickets)}
              icon={<Wrench className="w-6 h-6" />}
              color="red"
              trend={-2}
              trendLabel="resolved today"
              loading={loading}
            />
          </div>

          {/* Charts */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <OccupancyChart data={occupancyData} loading={loading} />
            <RevenueChart data={revenueData} loading={loading} />
          </div>

          {/* Quick Actions + Activity */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Quick Actions */}
            <div className="space-y-3">
              <h2 className="text-lg font-semibold text-foreground dark:text-white">Quick Actions</h2>
              <div className="grid grid-cols-1 gap-2">
                <Link href="/pricing">
                  <Button variant="outline" size="lg" className="w-full justify-start">
                    <Zap className="w-4 h-4 text-accent-400" /> Run Pricing Check
                  </Button>
                </Link>
                <Link href="/guests">
                  <Button variant="outline" size="lg" className="w-full justify-start">
                    <MessageSquare className="w-4 h-4 text-blue-500" /> View Guest Messages
                  </Button>
                </Link>
                <Link href="/reviews">
                  <Button variant="outline" size="lg" className="w-full justify-start">
                    <Star className="w-4 h-4 text-amber-500" /> Check Reviews
                  </Button>
                </Link>
                <Link href="/operations">
                  <Button variant="outline" size="lg" className="w-full justify-start">
                    <ClipboardList className="w-4 h-4 text-red-500" /> Add Maintenance Ticket
                  </Button>
                </Link>
              </div>
            </div>

            {/* Activity Feed */}
            <div className="lg:col-span-2">
              <ActivityFeed activity={activity} loading={loading} />
            </div>
          </div>
        </main>

        <MobileNav />
      </div>
    </div>
  );
}
