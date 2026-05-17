"use client";

import { useState } from "react";
import Sidebar from "@/components/layout/Sidebar";
import Header from "@/components/layout/Header";
import MobileNav from "@/components/layout/MobileNav";
import PricingTable from "@/components/pricing/PricingTable";
import CompetitorRatesCard from "@/components/pricing/CompetitorRatesCard";
import Button from "@/components/ui/Button";
import Badge from "@/components/ui/Badge";
import Card, { CardHeader } from "@/components/ui/Card";
import { runAgent } from "@/lib/api";
import { Zap, Calendar, TrendingUp } from "lucide-react";
import type { Hotel, PricingRecommendation } from "@/lib/types";

const DEMO_HOTELS: Hotel[] = [
  { id: "demo-1", name: "Kandy Heritage Villa", slug: "kandy-heritage-villa", city: "Kandy", total_rooms: 12, minimum_rate_lkr: 8000, amenities: [], is_active: true, created_at: "", updated_at: "" },
];

const DEMO_RECS: PricingRecommendation[] = [
  { room_type: "Standard Double", current_rate_lkr: 12000, recommended_rate_lkr: 14000, change_percent: 16.7, multiplier_applied: 1.3, reasoning: "Wesak Poya holiday — 1.3x multiplier applied. Occupancy at 75%." },
  { room_type: "Deluxe King", current_rate_lkr: 18000, recommended_rate_lkr: 21500, change_percent: 19.4, multiplier_applied: 1.3, reasoning: "Wesak Poya + high demand. Competitor rates averaging LKR 22,000." },
  { room_type: "Heritage Suite", current_rate_lkr: 28000, recommended_rate_lkr: 33000, change_percent: 17.9, multiplier_applied: 1.3, reasoning: "Premium suite — limited supply. Suggest premium positioning." },
  { room_type: "Family Room", current_rate_lkr: 22000, recommended_rate_lkr: 26500, change_percent: 20.5, multiplier_applied: 1.3, reasoning: "Family demand high during holiday. Only 1 room available." },
];

export default function PricingPage() {
  const [selectedHotel] = useState<Hotel>(DEMO_HOTELS[0]);
  const [recommendations, setRecommendations] = useState(DEMO_RECS);
  const [loading, setLoading] = useState(false);
  const [darkMode, setDarkMode] = useState(false);
  const [lastRun, setLastRun] = useState("2 hours ago");

  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
    document.documentElement.classList.toggle("dark");
  };

  const handleRunPricing = async () => {
    setLoading(true);
    try {
      const result = await runAgent({
        task: "daily_pricing_check",
        hotel_id: selectedHotel.id,
        agent_type: "pricing_agent",
      });
      if (result.data && (result.data as Record<string, unknown>).recommendations) {
        setRecommendations((result.data as Record<string, unknown>).recommendations as PricingRecommendation[]);
      }
      setLastRun("just now");
    } catch {
      // Keep demo data
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen bg-background dark:bg-gray-950">
      <Sidebar />
      <div className="flex-1 lg:ml-64">
        <Header hotels={DEMO_HOTELS} selectedHotel={selectedHotel} onSelectHotel={() => {}} darkMode={darkMode} onToggleDarkMode={toggleDarkMode} />
        <main className="p-4 md:p-6 lg:p-8 pb-24 lg:pb-8 space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-foreground dark:text-white">Pricing</h1>
              <p className="text-sm text-muted mt-1">AI-powered dynamic pricing recommendations</p>
            </div>
            <div className="flex items-center gap-3">
              <Badge variant="default" size="md">
                <Calendar className="w-3 h-3 mr-1" /> Last run: {lastRun}
              </Badge>
              <Button onClick={handleRunPricing} loading={loading}>
                <Zap className="w-4 h-4" /> Run Pricing Check
              </Button>
            </div>
          </div>

          {/* Demand Signal */}
          <Card padding="sm">
            <div className="flex items-center gap-4 px-4 py-3">
              <div className="w-10 h-10 rounded-xl bg-amber-100 dark:bg-amber-900/30 flex items-center justify-center">
                <TrendingUp className="w-5 h-5 text-amber-600" />
              </div>
              <div>
                <p className="text-sm font-semibold text-foreground dark:text-white">Demand Signal: High</p>
                <p className="text-xs text-muted">Wesak Poya holiday period detected. 1.3x multiplier auto-applied.</p>
              </div>
              <Badge variant="warning" size="md" className="ml-auto">HIGH</Badge>
            </div>
          </Card>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2">
              <PricingTable recommendations={recommendations} loading={loading} />
            </div>
            <div>
              <CompetitorRatesCard rates={[]} />
            </div>
          </div>
        </main>
        <MobileNav />
      </div>
    </div>
  );
}
