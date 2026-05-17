"use client";

import Card, { CardHeader } from "@/components/ui/Card";
import { formatLKR } from "@/lib/formatters";
import { Globe } from "lucide-react";

interface CompetitorRate {
  room_type: string;
  rate_lkr: number;
  source: string;
}

interface CompetitorRatesCardProps {
  rates: CompetitorRate[];
  loading?: boolean;
}

export default function CompetitorRatesCard({ rates, loading }: CompetitorRatesCardProps) {
  if (loading) {
    return (
      <Card>
        <CardHeader title="Competitor Rates" subtitle="OTA market comparison" />
        <div className="space-y-3 animate-pulse">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-12 bg-gray-100 dark:bg-gray-800 rounded-lg" />
          ))}
        </div>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader
        title="Competitor Rates"
        subtitle="OTA market comparison"
        action={<Globe className="w-5 h-5 text-muted" />}
      />
      {rates.length === 0 ? (
        <div className="text-center py-8">
          <Globe className="w-10 h-10 text-muted mx-auto mb-2 opacity-40" />
          <p className="text-sm text-muted">No competitor rates available</p>
          <p className="text-xs text-muted mt-1">Configure OTA URLs in settings to enable scraping</p>
        </div>
      ) : (
        <div className="space-y-3">
          {rates.map((rate, i) => (
            <div
              key={i}
              className="flex items-center justify-between p-3 rounded-xl bg-gray-50 dark:bg-gray-800/50"
            >
              <div>
                <p className="text-sm font-medium text-foreground dark:text-white">{rate.room_type}</p>
                <p className="text-xs text-muted capitalize">{rate.source}</p>
              </div>
              <p className="text-sm font-semibold text-foreground dark:text-white">
                {formatLKR(rate.rate_lkr)}
              </p>
            </div>
          ))}
        </div>
      )}
    </Card>
  );
}
