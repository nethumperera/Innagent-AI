"use client";

import {
  ResponsiveContainer, BarChart, Bar, XAxis, YAxis,
  CartesianGrid, Tooltip,
} from "recharts";
import Card, { CardHeader } from "@/components/ui/Card";
import { formatLKR } from "@/lib/formatters";

interface RevenueChartProps {
  data: { room_type: string; revenue: number }[];
  loading?: boolean;
}

export default function RevenueChart({ data, loading }: RevenueChartProps) {
  if (loading) {
    return (
      <Card>
        <CardHeader title="Revenue by Room Type" subtitle="Current period" />
        <div className="h-64 bg-gray-100 dark:bg-gray-800 rounded-lg animate-pulse" />
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader title="Revenue by Room Type" subtitle="Current period" />
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} barSize={40}>
            <defs>
              <linearGradient id="barGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#D4A017" stopOpacity={1} />
                <stop offset="100%" stopColor="#C49000" stopOpacity={0.8} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" vertical={false} />
            <XAxis
              dataKey="room_type"
              tick={{ fontSize: 11, fill: "#6B7280" }}
              axisLine={false}
              tickLine={false}
            />
            <YAxis
              tick={{ fontSize: 12, fill: "#6B7280" }}
              axisLine={false}
              tickLine={false}
              tickFormatter={(v) => `${(v / 1000).toFixed(0)}K`}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: "#1A1A1A",
                border: "none",
                borderRadius: "12px",
                color: "#fff",
                fontSize: "13px",
              }}
              formatter={(value: number) => [formatLKR(value), "Revenue"]}
            />
            <Bar
              dataKey="revenue"
              fill="url(#barGradient)"
              radius={[8, 8, 0, 0]}
            />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </Card>
  );
}
