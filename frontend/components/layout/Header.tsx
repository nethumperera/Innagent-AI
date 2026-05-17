"use client";

import { useState } from "react";
import { Moon, Sun, ChevronDown, Bell } from "lucide-react";
import type { Hotel } from "@/lib/types";

interface HeaderProps {
  hotels: Hotel[];
  selectedHotel: Hotel | null;
  onSelectHotel: (hotel: Hotel) => void;
  darkMode: boolean;
  onToggleDarkMode: () => void;
}

export default function Header({
  hotels, selectedHotel, onSelectHotel, darkMode, onToggleDarkMode,
}: HeaderProps) {
  const [dropdownOpen, setDropdownOpen] = useState(false);

  return (
    <header className="sticky top-0 z-30 bg-white/80 dark:bg-gray-900/80 backdrop-blur-md border-b border-gray-200 dark:border-gray-800">
      <div className="flex items-center justify-between px-6 py-3">
        {/* Left — Hotel Selector */}
        <div className="relative">
          <button
            onClick={() => setDropdownOpen(!dropdownOpen)}
            className="flex items-center gap-2 px-4 py-2 bg-gray-50 dark:bg-gray-800 rounded-xl hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
          >
            <div className="w-8 h-8 bg-primary-500 rounded-lg flex items-center justify-center text-white text-sm font-bold">
              {selectedHotel?.name?.[0] || "H"}
            </div>
            <div className="text-left">
              <p className="text-sm font-semibold text-foreground dark:text-white">
                {selectedHotel?.name || "Select Hotel"}
              </p>
              <p className="text-xs text-muted">{selectedHotel?.city || "—"}</p>
            </div>
            <ChevronDown className="w-4 h-4 text-muted ml-2" />
          </button>

          {dropdownOpen && (
            <div className="absolute top-full left-0 mt-2 w-72 bg-white dark:bg-gray-900 rounded-xl shadow-xl border border-gray-200 dark:border-gray-800 overflow-hidden z-50 animate-slide-up">
              {hotels.map((hotel) => (
                <button
                  key={hotel.id}
                  onClick={() => { onSelectHotel(hotel); setDropdownOpen(false); }}
                  className="w-full flex items-center gap-3 px-4 py-3 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors text-left"
                >
                  <div className="w-8 h-8 bg-primary-400 rounded-lg flex items-center justify-center text-white text-sm font-bold">
                    {hotel.name[0]}
                  </div>
                  <div>
                    <p className="text-sm font-medium text-foreground dark:text-white">{hotel.name}</p>
                    <p className="text-xs text-muted">{hotel.city} • {hotel.total_rooms} rooms</p>
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Right — Actions */}
        <div className="flex items-center gap-3">
          {/* Notifications */}
          <button className="relative p-2 rounded-xl hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors">
            <Bell className="w-5 h-5 text-muted" />
            <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-red-500 rounded-full" />
          </button>

          {/* Dark Mode Toggle */}
          <button
            onClick={onToggleDarkMode}
            className="p-2 rounded-xl hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
          >
            {darkMode ? (
              <Sun className="w-5 h-5 text-accent-400" />
            ) : (
              <Moon className="w-5 h-5 text-muted" />
            )}
          </button>

          {/* InnAgent Badge */}
          <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 bg-primary-50 dark:bg-primary-900/20 rounded-full">
            <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse" />
            <span className="text-xs font-medium text-primary-700 dark:text-primary-300">InnAgent AI</span>
          </div>
        </div>
      </div>
    </header>
  );
}
