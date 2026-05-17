"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { clsx } from "clsx";
import {
  LayoutDashboard, DollarSign, MessageSquare, Star,
  Wrench, Settings, Bot,
} from "lucide-react";

const navItems = [
  { href: "/", label: "Dashboard", icon: LayoutDashboard },
  { href: "/pricing", label: "Pricing", icon: DollarSign },
  { href: "/guests", label: "Guests", icon: MessageSquare },
  { href: "/reviews", label: "Reviews", icon: Star },
  { href: "/operations", label: "Operations", icon: Wrench },
  { href: "/settings", label: "Settings", icon: Settings },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="hidden lg:flex flex-col w-64 bg-primary-500 dark:bg-gray-950 text-white min-h-screen fixed left-0 top-0 z-40">
      {/* Logo */}
      <div className="px-6 py-6 border-b border-primary-400/30">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-accent-400 rounded-xl flex items-center justify-center shadow-lg">
            <Bot className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-lg font-bold tracking-tight">InnAgent AI</h1>
            <p className="text-xs text-primary-200 opacity-80">Co Host Ceylon</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-1">
        {navItems.map((item) => {
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={clsx(
                "flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-200",
                isActive
                  ? "bg-white/15 text-white shadow-sm backdrop-blur-sm"
                  : "text-primary-100 hover:bg-white/10 hover:text-white"
              )}
            >
              <item.icon className={clsx("w-5 h-5", isActive ? "text-accent-400" : "")} />
              {item.label}
              {isActive && (
                <div className="ml-auto w-1.5 h-1.5 bg-accent-400 rounded-full" />
              )}
            </Link>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="px-6 py-4 border-t border-primary-400/30">
        <div className="flex items-center gap-2 text-xs text-primary-200">
          <div className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse-slow" />
          <span>System Online</span>
        </div>
        <p className="text-[10px] text-primary-300 mt-1">
          © 2026 Co Host Ceylon
        </p>
      </div>
    </aside>
  );
}
