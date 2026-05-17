"use client";

import { useState } from "react";
import Sidebar from "@/components/layout/Sidebar";
import Header from "@/components/layout/Header";
import MobileNav from "@/components/layout/MobileNav";
import ConversationList from "@/components/guests/ConversationList";
import MessageBubble from "@/components/guests/MessageBubble";
import Card from "@/components/ui/Card";
import Badge from "@/components/ui/Badge";
import { MessageSquare } from "lucide-react";
import type { Hotel } from "@/lib/types";

const DEMO_HOTELS: Hotel[] = [
  { id: "demo-1", name: "Kandy Heritage Villa", slug: "kandy-heritage-villa", city: "Kandy", total_rooms: 12, minimum_rate_lkr: 8000, amenities: [], is_active: true, created_at: "", updated_at: "" },
];

const DEMO_CONVERSATIONS = [
  { guest_phone: "+44789012345", guest_name: "James Wilson", last_message: "Hi, do you have rooms available for Dec 25-28?", language: "english", timestamp: new Date(Date.now() - 1800000).toISOString(), unread: true },
  { guest_phone: "+94771234567", guest_name: undefined, last_message: "කරුණාකර මිල ගණන් දැනුම් දෙන්න", language: "sinhala", timestamp: new Date(Date.now() - 7200000).toISOString(), unread: false },
  { guest_phone: "+61412345678", guest_name: "Sarah Chen", last_message: "What time is check-in? And do you have airport transfers?", language: "english", timestamp: new Date(Date.now() - 14400000).toISOString(), unread: false },
];

const DEMO_MESSAGES = [
  { message: "Hi, do you have rooms available for December 25-28?", timestamp: new Date(Date.now() - 1800000).toISOString(), direction: "inbound" as const, language: "english" },
  { message: "Hello James! Thank you for reaching out to Kandy Heritage Villa! 🏨\n\nYes, we do have availability for December 25-28. Here are our options:\n\n• Standard Double — LKR 19,200/night + 12% VAT\n• Deluxe King — LKR 28,800/night + 12% VAT\n• Heritage Suite — LKR 44,800/night + 12% VAT\n\nPlease note these are our Christmas/New Year rates (peak season pricing applies).\n\nWould you like me to make a reservation?\n\nKandy Heritage Villa\nManaged by Co Host Ceylon | Powered by InnAgent AI", timestamp: new Date(Date.now() - 1700000).toISOString(), direction: "outbound" as const, agentUsed: "guest_bot" },
  { message: "The Deluxe King sounds perfect! Can I also book an airport transfer from Colombo?", timestamp: new Date(Date.now() - 1600000).toISOString(), direction: "inbound" as const, language: "english" },
];

export default function GuestsPage() {
  const [selectedHotel] = useState<Hotel>(DEMO_HOTELS[0]);
  const [selectedPhone, setSelectedPhone] = useState(DEMO_CONVERSATIONS[0].guest_phone);
  const [darkMode, setDarkMode] = useState(false);

  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
    document.documentElement.classList.toggle("dark");
  };

  return (
    <div className="flex min-h-screen bg-background dark:bg-gray-950">
      <Sidebar />
      <div className="flex-1 lg:ml-64">
        <Header hotels={DEMO_HOTELS} selectedHotel={selectedHotel} onSelectHotel={() => {}} darkMode={darkMode} onToggleDarkMode={toggleDarkMode} />
        <main className="p-4 md:p-6 lg:p-8 pb-24 lg:pb-8">
          <div className="mb-6">
            <h1 className="text-2xl font-bold text-foreground dark:text-white">Guest Messages</h1>
            <p className="text-sm text-muted mt-1">WhatsApp conversations managed by InnAgent AI</p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-[calc(100vh-220px)]">
            {/* Conversation List */}
            <Card padding="sm" className="overflow-y-auto">
              <div className="px-4 py-3 border-b border-gray-100 dark:border-gray-800">
                <div className="flex items-center gap-2">
                  <MessageSquare className="w-4 h-4 text-primary-500" />
                  <span className="text-sm font-semibold text-foreground dark:text-white">Conversations</span>
                  <Badge variant="info" size="sm">{DEMO_CONVERSATIONS.length}</Badge>
                </div>
              </div>
              <div className="p-2">
                <ConversationList
                  conversations={DEMO_CONVERSATIONS}
                  selectedPhone={selectedPhone}
                  onSelect={setSelectedPhone}
                />
              </div>
            </Card>

            {/* Message Thread */}
            <Card padding="sm" className="lg:col-span-2 flex flex-col">
              <div className="px-4 py-3 border-b border-gray-100 dark:border-gray-800">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-semibold text-foreground dark:text-white">
                      {DEMO_CONVERSATIONS.find(c => c.guest_phone === selectedPhone)?.guest_name || selectedPhone}
                    </p>
                    <p className="text-xs text-muted">{selectedPhone}</p>
                  </div>
                  <Badge variant="success" size="sm">AI Handled</Badge>
                </div>
              </div>
              <div className="flex-1 overflow-y-auto p-4">
                {DEMO_MESSAGES.map((msg, i) => (
                  <MessageBubble
                    key={i}
                    message={msg.message}
                    timestamp={msg.timestamp}
                    direction={msg.direction}
                    agentUsed={msg.direction === "outbound" ? "guest_bot" : undefined}
                    language={msg.direction === "inbound" ? "english" : undefined}
                  />
                ))}
              </div>
            </Card>
          </div>
        </main>
        <MobileNav />
      </div>
    </div>
  );
}
