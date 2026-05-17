"use client";

import { clsx } from "clsx";
import { formatTime } from "@/lib/formatters";
import { Bot, User } from "lucide-react";

interface MessageBubbleProps {
  message: string;
  timestamp: string;
  direction: "inbound" | "outbound";
  agentUsed?: string;
  language?: string;
}

export default function MessageBubble({
  message, timestamp, direction, agentUsed, language,
}: MessageBubbleProps) {
  const isGuest = direction === "inbound";

  return (
    <div className={clsx("flex gap-2 mb-4", isGuest ? "justify-start" : "justify-end")}>
      {isGuest && (
        <div className="w-8 h-8 rounded-full bg-gray-200 dark:bg-gray-700 flex items-center justify-center flex-shrink-0">
          <User className="w-4 h-4 text-muted" />
        </div>
      )}

      <div className={clsx("max-w-[75%]", isGuest ? "order-2" : "order-1")}>
        <div
          className={clsx(
            "px-4 py-3 rounded-2xl text-sm leading-relaxed",
            isGuest
              ? "bg-gray-100 dark:bg-gray-800 text-foreground dark:text-white rounded-tl-none"
              : "bg-primary-500 text-white rounded-tr-none"
          )}
        >
          {message}
        </div>
        <div className={clsx("flex items-center gap-2 mt-1", isGuest ? "" : "justify-end")}>
          <span className="text-[10px] text-muted">{formatTime(timestamp)}</span>
          {agentUsed && (
            <span className="text-[10px] text-primary-400 flex items-center gap-0.5">
              <Bot className="w-3 h-3" /> {agentUsed}
            </span>
          )}
          {language && language !== "english" && (
            <span className="text-[10px] text-accent-500 uppercase">{language}</span>
          )}
        </div>
      </div>

      {!isGuest && (
        <div className="w-8 h-8 rounded-full bg-primary-500 flex items-center justify-center flex-shrink-0 order-2">
          <Bot className="w-4 h-4 text-white" />
        </div>
      )}
    </div>
  );
}
