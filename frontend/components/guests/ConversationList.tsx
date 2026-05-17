"use client";

import { clsx } from "clsx";
import { formatRelativeTime } from "@/lib/formatters";
import { MessageSquare, Phone } from "lucide-react";
import Badge from "@/components/ui/Badge";

interface ConversationItem {
  guest_phone: string;
  guest_name?: string;
  last_message: string;
  language: string;
  timestamp: string;
  unread?: boolean;
}

interface ConversationListProps {
  conversations: ConversationItem[];
  selectedPhone?: string;
  onSelect: (phone: string) => void;
  loading?: boolean;
}

export default function ConversationList({
  conversations, selectedPhone, onSelect, loading,
}: ConversationListProps) {
  if (loading) {
    return (
      <div className="space-y-2">
        {[1, 2, 3, 4, 5].map((i) => (
          <div key={i} className="flex gap-3 p-3 animate-pulse">
            <div className="w-10 h-10 bg-gray-200 dark:bg-gray-700 rounded-full" />
            <div className="flex-1">
              <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-32 mb-2" />
              <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-48" />
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (conversations.length === 0) {
    return (
      <div className="text-center py-12">
        <MessageSquare className="w-10 h-10 text-muted mx-auto mb-3 opacity-40" />
        <p className="text-sm text-muted">No conversations yet</p>
        <p className="text-xs text-muted mt-1">Guest messages via WhatsApp will appear here</p>
      </div>
    );
  }

  return (
    <div className="space-y-1">
      {conversations.map((conv, i) => (
        <button
          key={i}
          onClick={() => onSelect(conv.guest_phone)}
          className={clsx(
            "w-full flex items-start gap-3 p-3 rounded-xl transition-colors text-left",
            selectedPhone === conv.guest_phone
              ? "bg-primary-50 dark:bg-primary-900/20 border border-primary-200 dark:border-primary-800"
              : "hover:bg-gray-50 dark:hover:bg-gray-800/50"
          )}
        >
          <div className="w-10 h-10 bg-primary-100 dark:bg-primary-900/30 rounded-full flex items-center justify-center flex-shrink-0">
            <Phone className="w-5 h-5 text-primary-600 dark:text-primary-400" />
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center justify-between">
              <p className="text-sm font-medium text-foreground dark:text-white truncate">
                {conv.guest_name || conv.guest_phone}
              </p>
              <span className="text-xs text-muted flex-shrink-0 ml-2">
                {formatRelativeTime(conv.timestamp)}
              </span>
            </div>
            <p className="text-xs text-muted truncate mt-0.5">{conv.last_message}</p>
            <div className="flex items-center gap-2 mt-1">
              <Badge size="sm" variant="outline">{conv.language}</Badge>
              {conv.unread && <div className="w-2 h-2 bg-accent-400 rounded-full" />}
            </div>
          </div>
        </button>
      ))}
    </div>
  );
}
