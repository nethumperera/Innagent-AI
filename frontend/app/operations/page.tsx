"use client";

import { useState } from "react";
import Sidebar from "@/components/layout/Sidebar";
import Header from "@/components/layout/Header";
import MobileNav from "@/components/layout/MobileNav";
import Card, { CardHeader } from "@/components/ui/Card";
import Badge from "@/components/ui/Badge";
import Button from "@/components/ui/Button";
import { getPriorityColor } from "@/lib/formatters";
import { Wrench, CheckCircle, Clock, AlertTriangle, Plus } from "lucide-react";
import type { Hotel, MaintenanceTicket } from "@/lib/types";

const DEMO_HOTELS: Hotel[] = [
  { id: "demo-1", name: "Kandy Heritage Villa", slug: "kandy-heritage-villa", city: "Kandy", total_rooms: 12, minimum_rate_lkr: 8000, amenities: [], is_active: true, created_at: "", updated_at: "" },
];

const DEMO_TICKETS: MaintenanceTicket[] = [
  { id: "t1", hotel_id: "demo-1", task_type: "maintenance", room: "Room 204", title: "A/C unit not cooling properly", description: "Guest reported room temperature not going below 26°C", priority: "urgent", assigned_to: "Kasun", status: "in_progress", due_by: new Date(Date.now() + 7200000).toISOString(), created_at: new Date(Date.now() - 14400000).toISOString() },
  { id: "t2", hotel_id: "demo-1", task_type: "housekeeping", room: "Room 108", title: "Checkout deep cleaning", description: "Full deep clean for checkout — VIP guest arriving tomorrow", priority: "high", assigned_to: "Nimali", status: "pending", due_by: new Date(Date.now() + 10800000).toISOString(), created_at: new Date(Date.now() - 3600000).toISOString() },
  { id: "t3", hotel_id: "demo-1", task_type: "maintenance", room: "Pool Area", title: "Pool pump pressure low", description: "Pressure gauge reading below normal. Schedule maintenance check.", priority: "medium", assigned_to: "Rajitha", status: "pending", due_by: new Date(Date.now() + 86400000).toISOString(), created_at: new Date(Date.now() - 28800000).toISOString() },
  { id: "t4", hotel_id: "demo-1", task_type: "inspection", room: "Room 301", title: "Pre-arrival inspection", description: "Check room readiness for confirmed booking tomorrow.", priority: "medium", assigned_to: "Nimali", status: "pending", due_by: new Date(Date.now() + 43200000).toISOString(), created_at: new Date(Date.now() - 1800000).toISOString() },
  { id: "t5", hotel_id: "demo-1", task_type: "housekeeping", room: "Room 105", title: "Linen replacement", description: "Replace bedsheets and towels — standard daily service.", priority: "low", assigned_to: "Dilani", status: "completed", completed_at: new Date(Date.now() - 7200000).toISOString(), created_at: new Date(Date.now() - 18000000).toISOString() },
];

const statusIcons: Record<string, typeof CheckCircle> = {
  pending: Clock,
  in_progress: Wrench,
  completed: CheckCircle,
  overdue: AlertTriangle,
};

const statusColors: Record<string, string> = {
  pending: "warning",
  in_progress: "info",
  completed: "success",
  overdue: "danger",
};

export default function OperationsPage() {
  const [selectedHotel] = useState<Hotel>(DEMO_HOTELS[0]);
  const [tickets] = useState(DEMO_TICKETS);
  const [darkMode, setDarkMode] = useState(false);
  const [filter, setFilter] = useState("all");

  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
    document.documentElement.classList.toggle("dark");
  };

  const filtered = filter === "all" ? tickets : tickets.filter(t => t.status === filter);
  const urgentCount = tickets.filter(t => t.priority === "urgent").length;
  const pendingCount = tickets.filter(t => t.status === "pending").length;
  const completedCount = tickets.filter(t => t.status === "completed").length;

  return (
    <div className="flex min-h-screen bg-background dark:bg-gray-950">
      <Sidebar />
      <div className="flex-1 lg:ml-64">
        <Header hotels={DEMO_HOTELS} selectedHotel={selectedHotel} onSelectHotel={() => {}} darkMode={darkMode} onToggleDarkMode={toggleDarkMode} />
        <main className="p-4 md:p-6 lg:p-8 pb-24 lg:pb-8 space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-foreground dark:text-white">Operations</h1>
              <p className="text-sm text-muted mt-1">Housekeeping tasks & maintenance tickets</p>
            </div>
            <Button><Plus className="w-4 h-4" /> New Ticket</Button>
          </div>

          {/* Stats Row */}
          <div className="grid grid-cols-3 gap-4">
            <Card padding="sm">
              <div className="flex items-center gap-3 px-2">
                <div className="w-10 h-10 rounded-xl bg-red-100 dark:bg-red-900/30 flex items-center justify-center">
                  <AlertTriangle className="w-5 h-5 text-red-600" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-foreground dark:text-white">{urgentCount}</p>
                  <p className="text-xs text-muted">Urgent</p>
                </div>
              </div>
            </Card>
            <Card padding="sm">
              <div className="flex items-center gap-3 px-2">
                <div className="w-10 h-10 rounded-xl bg-amber-100 dark:bg-amber-900/30 flex items-center justify-center">
                  <Clock className="w-5 h-5 text-amber-600" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-foreground dark:text-white">{pendingCount}</p>
                  <p className="text-xs text-muted">Pending</p>
                </div>
              </div>
            </Card>
            <Card padding="sm">
              <div className="flex items-center gap-3 px-2">
                <div className="w-10 h-10 rounded-xl bg-emerald-100 dark:bg-emerald-900/30 flex items-center justify-center">
                  <CheckCircle className="w-5 h-5 text-emerald-600" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-foreground dark:text-white">{completedCount}</p>
                  <p className="text-xs text-muted">Completed</p>
                </div>
              </div>
            </Card>
          </div>

          {/* Filter Tabs */}
          <div className="flex gap-2">
            {["all", "pending", "in_progress", "completed"].map(f => (
              <button key={f} onClick={() => setFilter(f)}
                className={`px-4 py-2 rounded-xl text-sm font-medium transition-colors ${filter === f ? "bg-primary-500 text-white" : "bg-gray-100 dark:bg-gray-800 text-muted hover:text-foreground"}`}
              >{f === "all" ? "All" : f.replace("_", " ").replace(/\b\w/g, l => l.toUpperCase())}</button>
            ))}
          </div>

          {/* Tickets List */}
          <div className="space-y-3">
            {filtered.map(ticket => {
              const StatusIcon = statusIcons[ticket.status] || Clock;
              return (
                <Card key={ticket.id} hover padding="sm">
                  <div className="flex items-center gap-4 px-2">
                    <StatusIcon className={`w-5 h-5 flex-shrink-0`} style={{ color: getPriorityColor(ticket.priority) }} />
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <p className="text-sm font-semibold text-foreground dark:text-white truncate">{ticket.title}</p>
                        <Badge variant={statusColors[ticket.status] as "warning" | "info" | "success" | "danger"} size="sm">{ticket.status}</Badge>
                      </div>
                      <div className="flex items-center gap-3 mt-1">
                        <span className="text-xs text-muted">{ticket.room}</span>
                        <span className="text-xs text-muted">•</span>
                        <span className="text-xs text-muted capitalize">{ticket.task_type}</span>
                        <span className="text-xs text-muted">•</span>
                        <span className="text-xs text-muted">Assigned: {ticket.assigned_to}</span>
                      </div>
                    </div>
                    <Badge variant={ticket.priority === "urgent" ? "danger" : ticket.priority === "high" ? "warning" : "default"} size="md">
                      {ticket.priority}
                    </Badge>
                  </div>
                </Card>
              );
            })}
          </div>
        </main>
        <MobileNav />
      </div>
    </div>
  );
}
