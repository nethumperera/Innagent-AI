"use client";

import Card, { CardHeader } from "@/components/ui/Card";
import Badge from "@/components/ui/Badge";
import { formatRelativeTime } from "@/lib/formatters";
import { Bot, DollarSign, MessageSquare, Star, Wrench } from "lucide-react";
import type { AgentLog } from "@/lib/types";

interface ActivityFeedProps {
  activity: AgentLog[];
  loading?: boolean;
}

const agentIcons: Record<string, typeof Bot> = {
  pricing_agent: DollarSign,
  guest_bot: MessageSquare,
  revenue_agent: Bot,
  review_agent: Star,
  operations_agent: Wrench,
  orchestrator: Bot,
};

const agentColors: Record<string, string> = {
  pricing_agent: "bg-emerald-100 text-emerald-600 dark:bg-emerald-900/30 dark:text-emerald-400",
  guest_bot: "bg-blue-100 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400",
  revenue_agent: "bg-purple-100 text-purple-600 dark:bg-purple-900/30 dark:text-purple-400",
  review_agent: "bg-amber-100 text-amber-600 dark:bg-amber-900/30 dark:text-amber-400",
  operations_agent: "bg-red-100 text-red-600 dark:bg-red-900/30 dark:text-red-400",
};

export default function ActivityFeed({ activity, loading }: ActivityFeedProps) {
  if (loading) {
    return (
      <Card>
        <CardHeader title="Recent Activity" subtitle="Last 10 agent actions" />
        <div className="space-y-3">
          {[1, 2, 3, 4, 5].map((i) => (
            <div key={i} className="flex gap-3 animate-pulse">
              <div className="w-9 h-9 bg-gray-200 dark:bg-gray-700 rounded-xl" />
              <div className="flex-1">
                <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-3/4 mb-2" />
                <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-1/2" />
              </div>
            </div>
          ))}
        </div>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader title="Recent Activity" subtitle="Last 10 agent actions" />
      <div className="space-y-3 max-h-96 overflow-y-auto">
        {activity.length === 0 ? (
          <p className="text-sm text-muted text-center py-8">No recent activity</p>
        ) : (
          activity.map((log, i) => {
            const IconComponent = agentIcons[log.agent_name] || Bot;
            const colorClass = agentColors[log.agent_name] || "bg-gray-100 text-gray-600";
            return (
              <div
                key={log.id || i}
                className="flex items-start gap-3 p-3 rounded-xl hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors"
              >
                <div className={`w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0 ${colorClass}`}>
                  <IconComponent className="w-4 h-4" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-foreground dark:text-white truncate">
                    {log.task}
                  </p>
                  <div className="flex items-center gap-2 mt-1">
                    <Badge variant={log.escalated ? "warning" : "default"} size="sm">
                      {log.agent_name?.replace("_", " ")}
                    </Badge>
                    <span className="text-xs text-muted">
                      {formatRelativeTime(log.created_at)}
                    </span>
                  </div>
                </div>
                {log.confidence !== undefined && (
                  <span className="text-xs text-muted font-mono">
                    {(log.confidence * 100).toFixed(0)}%
                  </span>
                )}
              </div>
            );
          })
        )}
      </div>
    </Card>
  );
}
