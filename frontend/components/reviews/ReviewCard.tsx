"use client";

import Card from "@/components/ui/Card";
import Badge from "@/components/ui/Badge";
import Button from "@/components/ui/Button";
import { formatDate, getSentimentColor, getPriorityColor } from "@/lib/formatters";
import { Star, AlertTriangle, ExternalLink } from "lucide-react";
import type { Review } from "@/lib/types";

interface ReviewCardProps {
  review: Review;
  onApprove?: (id: string) => void;
  onEdit?: (id: string) => void;
  onReject?: (id: string) => void;
}

export default function ReviewCard({ review, onApprove, onEdit, onReject }: ReviewCardProps) {
  const stars = Array.from({ length: 5 }, (_, i) => i < review.star_rating);

  const sentimentVariant = {
    positive: "success" as const,
    neutral: "default" as const,
    negative: "danger" as const,
    mixed: "warning" as const,
  };

  const urgencyVariant = {
    low: "default" as const,
    medium: "info" as const,
    high: "warning" as const,
    critical: "danger" as const,
  };

  return (
    <Card hover>
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div>
          <div className="flex items-center gap-2">
            <p className="text-sm font-semibold text-foreground dark:text-white">
              {review.reviewer_name || "Anonymous"}
            </p>
            <Badge variant={sentimentVariant[review.sentiment as keyof typeof sentimentVariant] || "default"}>
              {review.sentiment}
            </Badge>
          </div>
          <div className="flex items-center gap-2 mt-1">
            <div className="flex gap-0.5">
              {stars.map((filled, i) => (
                <Star
                  key={i}
                  className={`w-3.5 h-3.5 ${filled ? "text-accent-400 fill-accent-400" : "text-gray-300 dark:text-gray-600"}`}
                />
              ))}
            </div>
            <span className="text-xs text-muted">{review.platform}</span>
            <span className="text-xs text-muted">•</span>
            <span className="text-xs text-muted">{formatDate(review.created_at)}</span>
          </div>
        </div>
        <Badge variant={urgencyVariant[review.urgency as keyof typeof urgencyVariant] || "default"} size="md">
          {review.urgency === "critical" && <AlertTriangle className="w-3 h-3 mr-1" />}
          {review.urgency}
        </Badge>
      </div>

      {/* Review Text */}
      <div className="bg-gray-50 dark:bg-gray-800/50 rounded-xl p-4 mb-4">
        <p className="text-sm text-foreground dark:text-gray-300 italic leading-relaxed">
          &ldquo;{review.review_text}&rdquo;
        </p>
      </div>

      {/* Issues */}
      {review.issues_mentioned && review.issues_mentioned.length > 0 && (
        <div className="flex flex-wrap gap-1.5 mb-4">
          {review.issues_mentioned.map((issue, i) => (
            <Badge key={i} variant="outline" size="sm">{issue}</Badge>
          ))}
        </div>
      )}

      {/* Draft Response */}
      {review.response_draft && (
        <div className="border border-primary-200 dark:border-primary-800 bg-primary-50 dark:bg-primary-900/10 rounded-xl p-4 mb-4">
          <p className="text-xs font-semibold text-primary-600 dark:text-primary-400 mb-1">
            AI Draft Response
          </p>
          <p className="text-sm text-foreground dark:text-gray-300 leading-relaxed">
            {review.response_draft}
          </p>
        </div>
      )}

      {/* Actions */}
      {review.response_status !== "posted" && review.response_status !== "approved" && (
        <div className="flex items-center gap-2 pt-2 border-t border-gray-100 dark:border-gray-800">
          <Button size="sm" variant="primary" onClick={() => onApprove?.(review.id)}>
            Approve
          </Button>
          <Button size="sm" variant="outline" onClick={() => onEdit?.(review.id)}>
            Edit
          </Button>
          <Button size="sm" variant="ghost" onClick={() => onReject?.(review.id)}>
            Skip
          </Button>
          <div className="flex-1" />
          <Badge variant={review.response_status === "draft_ready" ? "success" : "default"} size="md">
            {review.response_status}
          </Badge>
        </div>
      )}
    </Card>
  );
}
