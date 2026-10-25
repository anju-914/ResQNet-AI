"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Map, ListChecks, Radio, Send, Activity } from "lucide-react";

export default function LeftRail() {
  const pathname = usePathname();

  const navItems = [
    { label: "Map", href: "/", icon: Map },
    { label: "Queue", href: "/queue", icon: ListChecks },
    { label: "Incidents", href: "/incidents", icon: Activity },
    { label: "Submit SOS", href: "/submit", icon: Send },
  ];

  return (
    <aside className="w-[72px] border-r border-white/10 bg-[#0a0a0a] flex flex-col items-center py-4 gap-2 z-20 select-none">
      {navItems.map((item) => {
        const Icon = item.icon;
        const isActive = pathname === item.href;

        return (
          <Link
            key={item.href}
            href={item.href}
            className={`w-full flex flex-col items-center justify-center py-3 px-1 gap-1 text-[11px] font-medium transition-all relative ${
              isActive
                ? "text-white bg-white/5"
                : "text-white/50 hover:text-white/80 hover:bg-white/[0.02]"
            }`}
          >
            {/* Active gold left indicator bar */}
            {isActive && (
              <span className="absolute left-0 top-0 bottom-0 w-1 bg-gold rounded-r" />
            )}
            <Icon
              className={`w-5 h-5 ${
                isActive ? "text-gold" : "text-white/50 group-hover:text-white/80"
              }`}
            />
            <span>{item.label}</span>
          </Link>
        );
      })}
    </aside>
  );
}

