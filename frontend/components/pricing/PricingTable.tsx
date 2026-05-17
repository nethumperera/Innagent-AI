"use client";

import Card from "@/components/ui/Card";
import Badge from "@/components/ui/Badge";
import Button from "@/components/ui/Button";
import { formatLKR } from "@/lib/formatters";
import { TrendingUp, TrendingDown, Minus } from "lucide-react";
import type { PricingRecommendation } from "@/lib/types";

interface PricingTableProps {
  recommendations: PricingRecommendation[];
  loading?: boolean;
  onApprove?: (rec: PricingRecommendation) => void;
}

export default function PricingTable({ recommendations, loading, onApprove }: PricingTableProps) {
  if (loading) {
    return (
      <Card>
        <div className="space-y-4 animate-pulse">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-16 bg-gray-100 dark:bg-gray-800 rounded-lg" />
          ))}
        </div>
      </Card>
    );
  }

  return (
    <Card padding="sm">
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-gray-200 dark:border-gray-800">
              <th className="text-left px-4 py-3 text-xs font-semibold text-muted uppercase tracking-wider">Room Type</th>
              <th className="text-right px-4 py-3 text-xs font-semibold text-muted uppercase tracking-wider">Current Rate</th>
              <th className="text-right px-4 py-3 text-xs font-semibold text-muted uppercase tracking-wider">Recommended</th>
              <th className="text-center px-4 py-3 text-xs font-semibold text-muted uppercase tracking-wider">Change</th>
              <th className="text-center px-4 py-3 text-xs font-semibold text-muted uppercase tracking-wider">Multiplier</th>
              <th className="text-right px-4 py-3 text-xs font-semibold text-muted uppercase tracking-wider">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100 dark:divide-gray-800">
            {recommendations.map((rec, i) => (
              <tr key={i} className="hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors">
                <td className="px-4 py-4">
                  <p className="text-sm font-medium text-foreground dark:text-white">{rec.room_type}</p>
                </td>
                <td className="px-4 py-4 text-right">
                  <p className="text-sm text-muted">{formatLKR(rec.current_rate_lkr)}</p>
                </td>
                <td className="px-4 py-4 text-right">
                  <p className="text-sm font-semibold text-foreground dark:text-white">{formatLKR(rec.recommended_rate_lkr)}</p>
                </td>
                <td className="px-4 py-4 text-center">
                  <div className="flex items-center justify-center gap-1">
                    {rec.change_percent > 0 ? (
                      <TrendingUp className="w-4 h-4 text-emerald-500" />
                    ) : rec.change_percent < 0 ? (
                      <TrendingDown className="w-4 h-4 text-red-500" />
                    ) : (
                      <Minus className="w-4 h-4 text-muted" />
                    )}
                    <Badge variant={rec.change_percent > 0 ? "success" : rec.change_percent < 0 ? "danger" : "default"}>
                      {rec.change_percent > 0 ? "+" : ""}{rec.change_percent.toFixed(1)}%
                    </Badge>
                  </div>
                </td>
                <td className="px-4 py-4 text-center">
                  <Badge variant="info">{rec.multiplier_applied}x</Badge>
                </td>
                <td className="px-4 py-4 text-right">
                  <Button size="sm" variant="outline" onClick={() => onApprove?.(rec)}>
                    Apply
                  </Button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Card>
  );
}
