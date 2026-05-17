// ════════════════════════════════════════════════════════════════
// InnAgent AI — Formatters
// LKR currency, date, and percentage formatters
// ════════════════════════════════════════════════════════════════

/**
 * Format a number as LKR currency with comma separators.
 * e.g., 14500 → "LKR 14,500"
 */
export function formatLKR(amount: number): string {
  if (amount === null || amount === undefined) return "LKR 0";
  return `LKR ${Math.round(amount).toLocaleString("en-LK")}`;
}

/**
 * Format a number as a short LKR amount.
 * e.g., 1450000 → "LKR 1.45M"
 */
export function formatLKRShort(amount: number): string {
  if (amount >= 1_000_000) return `LKR ${(amount / 1_000_000).toFixed(1)}M`;
  if (amount >= 1_000) return `LKR ${(amount / 1_000).toFixed(0)}K`;
  return formatLKR(amount);
}

/**
 * Format a percentage with one decimal place.
 * e.g., 78.5 → "78.5%"
 */
export function formatPercent(value: number): string {
  if (value === null || value === undefined) return "0%";
  return `${value.toFixed(1)}%`;
}

/**
 * Format a date string to a readable format.
 * e.g., "2026-05-17T10:30:00" → "May 17, 2026"
 */
export function formatDate(dateStr: string): string {
  if (!dateStr) return "";
  const d = new Date(dateStr);
  return d.toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

/**
 * Format a date string to relative time.
 * e.g., "2 hours ago", "just now"
 */
export function formatRelativeTime(dateStr: string): string {
  if (!dateStr) return "";
  const now = new Date();
  const d = new Date(dateStr);
  const diffMs = now.getTime() - d.getTime();
  const diffMin = Math.floor(diffMs / 60000);
  const diffHr = Math.floor(diffMin / 60);
  const diffDay = Math.floor(diffHr / 24);

  if (diffMin < 1) return "just now";
  if (diffMin < 60) return `${diffMin}m ago`;
  if (diffHr < 24) return `${diffHr}h ago`;
  if (diffDay < 7) return `${diffDay}d ago`;
  return formatDate(dateStr);
}

/**
 * Format a timestamp to time only.
 * e.g., "10:30 AM"
 */
export function formatTime(dateStr: string): string {
  if (!dateStr) return "";
  const d = new Date(dateStr);
  return d.toLocaleTimeString("en-US", {
    hour: "numeric",
    minute: "2-digit",
    hour12: true,
  });
}

/**
 * Get a color based on occupancy rate.
 */
export function getOccupancyColor(rate: number): string {
  if (rate >= 85) return "#10B981"; // green
  if (rate >= 60) return "#D4A017"; // gold
  if (rate >= 40) return "#F59E0B"; // amber
  return "#EF4444"; // red
}

/**
 * Get a color based on sentiment.
 */
export function getSentimentColor(sentiment: string): string {
  switch (sentiment) {
    case "positive": return "#10B981";
    case "neutral": return "#6B7280";
    case "negative": return "#EF4444";
    case "mixed": return "#F59E0B";
    default: return "#6B7280";
  }
}

/**
 * Get a color based on priority.
 */
export function getPriorityColor(priority: string): string {
  switch (priority) {
    case "urgent": return "#EF4444";
    case "high": return "#F59E0B";
    case "medium": return "#3B82F6";
    case "low": return "#10B981";
    default: return "#6B7280";
  }
}
