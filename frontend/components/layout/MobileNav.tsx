"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { clsx } from "clsx";
import {
  LayoutDashboard, DollarSign, MessageSquare, Star, Wrench,
} from "lucide-react";

const mobileNavItems = [
  { href: "/", label: "Home", icon: LayoutDashboard },
  { href: "/pricing", label: "Pricing", icon: DollarSign },
  { href: "/guests", label: "Guests", icon: MessageSquare },
  { href: "/reviews", label: "Reviews", icon: Star },
  { href: "/operations", label: "Ops", icon: Wrench },
];

export default function MobileNav() {
  const pathname = usePathname();

  return (
    <nav className="lg:hidden fixed bottom-0 left-0 right-0 z-50 bg-white dark:bg-gray-900 border-t border-gray-200 dark:border-gray-800 safe-area-pb">
      <div className="flex items-center justify-around py-2">
        {mobileNavItems.map((item) => {
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={clsx(
                "flex flex-col items-center gap-1 px-3 py-1.5 rounded-xl transition-colors",
                isActive
                  ? "text-primary-500 dark:text-accent-400"
                  : "text-muted hover:text-foreground dark:hover:text-white"
              )}
            >
              <item.icon className="w-5 h-5" />
              <span className="text-[10px] font-medium">{item.label}</span>
              {isActive && <div className="w-1 h-1 bg-accent-400 rounded-full" />}
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
