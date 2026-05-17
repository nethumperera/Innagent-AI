"use client";

import { clsx } from "clsx";
import { TrendingUp, TrendingDown, Minus } from "lucide-react";
import type { ReactNode } from "react";

interface KPICardProps {
  title: string;
  value: string;
  icon: ReactNode;
  trend?: number;
  trendLabel?: string;
  color?: string;
  loading?: boolean;
}

export default function KPICard({
  title, value, icon, trend, trendLabel, color = "primary", loading = false,
}: KPICardProps) {
  const colorClasses: Record<string, string> = {
    primary: "from-primary-500 to-primary-600",
    gold: "from-accent-400 to-accent-500",
    emerald: "from-emerald-500 to-emerald-600",
    red: "from-red-500 to-red-600",
  };

  if (loading) {
    return (
      <div className="bg-white dark:bg-gray-900 rounded-2xl border border-gray-200 dark:border-gray-800 p-6 animate-pulse">
        <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-24 mb-4" />
        <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded w-32 mb-2" />
        <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-20" />
      </div>
    );
  }

  return (
    <div className="bg-white dark:bg-gray-900 rounded-2xl border border-gray-200 dark:border-gray-800 p-6 hover:shadow-lg transition-all duration-300 group">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm font-medium text-muted mb-1">{title}</p>
          <p className="text-3xl font-bold text-foreground dark:text-white tracking-tight">
            {value}
          </p>
        </div>
        <div
          className={clsx(
            "w-12 h-12 rounded-2xl bg-gradient-to-br flex items-center justify-center text-white shadow-lg group-hover:scale-110 transition-transform duration-300",
            colorClasses[color] || colorClasses.primary
          )}
        >
          {icon}
        </div>
      </div>

      {trend !== undefined && (
        <div className="flex items-center gap-1.5 mt-3">
          {trend > 0 ? (
            <TrendingUp className="w-4 h-4 text-emerald-500" />
          ) : trend < 0 ? (
            <TrendingDown className="w-4 h-4 text-red-500" />
          ) : (
            <Minus className="w-4 h-4 text-muted" />
          )}
          <span
            className={clsx(
              "text-sm font-medium",
              trend > 0 ? "text-emerald-600" : trend < 0 ? "text-red-600" : "text-muted"
            )}
          >
            {trend > 0 ? "+" : ""}{trend}%
          </span>
          {trendLabel && (
            <span className="text-xs text-muted ml-1">{trendLabel}</span>
          )}
        </div>
      )}
    </div>
  );
}
