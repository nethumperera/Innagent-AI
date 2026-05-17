"use client";

import { useState, useEffect } from "react";
import Sidebar from "@/components/layout/Sidebar";
import Header from "@/components/layout/Header";
import MobileNav from "@/components/layout/MobileNav";
import ConversationList from "@/components/guests/ConversationList";
import MessageBubble from "@/components/guests/MessageBubble";
import Card from "@/components/ui/Card";
import Badge from "@/components/ui/Badge";
import { MessageSquare, Loader2 } from "lucide-react";
import type { Hotel, ConversationItem } from "@/lib/types";
import { fetchHotels, fetchConversations, fetchConversationThread } from "@/lib/api";

export default function GuestsPage() {
  const [hotels, setHotels] = useState<Hotel[]>([]);
  const [selectedHotel, setSelectedHotel] = useState<Hotel | null>(null);
  
  const [conversations, setConversations] = useState<ConversationItem[]>([]);
  const [selectedPhone, setSelectedPhone] = useState<string | null>(null);
  const [messages, setMessages] = useState<any[]>([]);
  
  const [loadingConv, setLoadingConv] = useState(true);
  const [loadingMessages, setLoadingMessages] = useState(false);
  const [darkMode, setDarkMode] = useState(false);

  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
    document.documentElement.classList.toggle("dark");
  };

  // Initial Load: Fetch Hotels
  useEffect(() => {
    fetchHotels().then((data) => {
      setHotels(data);
      if (data.length > 0) {
        setSelectedHotel(data[0]);
      } else {
        setLoadingConv(false);
      }
    });
  }, []);

  // Fetch conversations when hotel changes
  useEffect(() => {
    if (!selectedHotel) return;
    setLoadingConv(true);
    fetchConversations(selectedHotel.id).then((data) => {
      setConversations(data);
      setLoadingConv(false);
      // Auto-select first conversation
      if (data.length > 0 && !selectedPhone) {
        setSelectedPhone(data[0].guest_phone);
      }
    });
  }, [selectedHotel]);

  // Fetch thread when conversation is selected
  useEffect(() => {
    if (!selectedHotel || !selectedPhone) return;
    setLoadingMessages(true);
    
    // Poll every 5 seconds for new messages
    const fetchThread = () => {
      fetchConversationThread(selectedHotel.id, selectedPhone).then((data) => {
        setMessages(data);
        setLoadingMessages(false);
      });
    };
    
    fetchThread();
    const interval = setInterval(fetchThread, 5000);
    return () => clearInterval(interval);
  }, [selectedHotel, selectedPhone]);

  if (!selectedHotel) {
    return (
      <div className="flex min-h-screen bg-background dark:bg-gray-950 items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-primary-500" />
      </div>
    );
  }

  return (
    <div className="flex min-h-screen bg-background dark:bg-gray-950">
      <Sidebar />
      <div className="flex-1 lg:ml-64">
        <Header hotels={hotels} selectedHotel={selectedHotel} onSelectHotel={setSelectedHotel} darkMode={darkMode} onToggleDarkMode={toggleDarkMode} />
        <main className="p-4 md:p-6 lg:p-8 pb-24 lg:pb-8">
          <div className="mb-6">
            <h1 className="text-2xl font-bold text-foreground dark:text-white">Guest Messages</h1>
            <p className="text-sm text-muted mt-1">Live WhatsApp conversations managed by InnAgent AI</p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-[calc(100vh-220px)]">
            {/* Conversation List */}
            <Card padding="sm" className="overflow-y-auto">
              <div className="px-4 py-3 border-b border-gray-100 dark:border-gray-800">
                <div className="flex items-center gap-2">
                  <MessageSquare className="w-4 h-4 text-primary-500" />
                  <span className="text-sm font-semibold text-foreground dark:text-white">Conversations</span>
                  <Badge variant="info" size="sm">{conversations.length}</Badge>
                </div>
              </div>
              <div className="p-2">
                {loadingConv ? (
                  <div className="flex justify-center p-8"><Loader2 className="w-6 h-6 animate-spin text-gray-400" /></div>
                ) : conversations.length === 0 ? (
                  <div className="text-center p-8 text-muted text-sm">No conversations found.</div>
                ) : (
                  <ConversationList
                    conversations={conversations}
                    selectedPhone={selectedPhone || ""}
                    onSelect={setSelectedPhone}
                  />
                )}
              </div>
            </Card>

            {/* Message Thread */}
            <Card padding="sm" className="lg:col-span-2 flex flex-col">
              <div className="px-4 py-3 border-b border-gray-100 dark:border-gray-800">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-semibold text-foreground dark:text-white">
                      {conversations.find(c => c.guest_phone === selectedPhone)?.guest_name || selectedPhone || "Select a chat"}
                    </p>
                    <p className="text-xs text-muted">{selectedPhone}</p>
                  </div>
                  {selectedPhone && <Badge variant="success" size="sm">Live Feed</Badge>}
                </div>
              </div>
              
              <div className="flex-1 overflow-y-auto p-4 flex flex-col-reverse">
                {/* flex-col-reverse handles the scrolling to bottom automatically if we reverse the array, 
                    but since our DB order is oldest first, we render normally and rely on the UI */}
                <div className="space-y-4">
                  {loadingMessages && messages.length === 0 ? (
                    <div className="flex justify-center p-8"><Loader2 className="w-6 h-6 animate-spin text-gray-400" /></div>
                  ) : (
                    messages.map((msg, i) => (
                      <MessageBubble
                        key={msg.id || i}
                        message={msg.message_body}
                        timestamp={msg.created_at}
                        direction={msg.direction}
                        agentUsed={msg.agent_used}
                        language={msg.language}
                      />
                    ))
                  )}
                </div>
              </div>
            </Card>
          </div>
        </main>
        <MobileNav />
      </div>
    </div>
  );
}
