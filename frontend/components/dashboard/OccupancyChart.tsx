"use client";

import {
  ResponsiveContainer, LineChart, Line, XAxis, YAxis,
  CartesianGrid, Tooltip, Area, AreaChart,
} from "recharts";
import Card, { CardHeader } from "@/components/ui/Card";

interface OccupancyChartProps {
  data: { date: string; occupancy: number }[];
  loading?: boolean;
}

export default function OccupancyChart({ data, loading }: OccupancyChartProps) {
  if (loading) {
    return (
      <Card>
        <CardHeader title="Occupancy Rate" subtitle="Last 7 days" />
        <div className="h-64 bg-gray-100 dark:bg-gray-800 rounded-lg animate-pulse" />
      </Card>
    );
  }

  const formattedData = data.map((d) => ({
    ...d,
    date: new Date(d.date).toLocaleDateString("en-US", { weekday: "short", month: "short", day: "numeric" }),
  }));

  return (
    <Card>
      <CardHeader title="Occupancy Rate" subtitle="Last 7 days" />
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={formattedData}>
            <defs>
              <linearGradient id="occupancyGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#1B4332" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#1B4332" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" vertical={false} />
            <XAxis
              dataKey="date"
              tick={{ fontSize: 12, fill: "#6B7280" }}
              axisLine={false}
              tickLine={false}
            />
            <YAxis
              tick={{ fontSize: 12, fill: "#6B7280" }}
              axisLine={false}
              tickLine={false}
              domain={[0, 100]}
              tickFormatter={(v) => `${v}%`}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: "#1A1A1A",
                border: "none",
                borderRadius: "12px",
                color: "#fff",
                fontSize: "13px",
              }}
              formatter={(value: number) => [`${value.toFixed(1)}%`, "Occupancy"]}
            />
            <Area
              type="monotone"
              dataKey="occupancy"
              stroke="#1B4332"
              strokeWidth={3}
              fill="url(#occupancyGradient)"
              dot={{ r: 4, fill: "#1B4332", strokeWidth: 2, stroke: "#fff" }}
              activeDot={{ r: 6, fill: "#D4A017", stroke: "#fff", strokeWidth: 2 }}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </Card>
  );
}
