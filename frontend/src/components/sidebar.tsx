"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";

const nav = [
  { href: "/", label: "Dashboard", icon: "⊞" },
  { href: "/projects", label: "Projects", icon: "◈" },
  { href: "/agents", label: "Agents", icon: "◇" },
  { href: "/tasks", label: "Tasks", icon: "☰" },
  { href: "/memory", label: "Memory", icon: "◎" },
];

export function Sidebar() {
  const path = usePathname();

  return (
    <aside className="fixed left-0 top-0 bottom-0 w-60 bg-surface border-r border-border flex flex-col z-50">
      <div className="p-6 border-b border-border">
        <Link href="/" className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-accent flex items-center justify-center text-black font-mono font-bold text-sm">C</div>
          <div>
            <div className="font-bold text-sm tracking-wide">CAMera</div>
            <div className="text-[10px] text-muted font-mono">v1.0.0</div>
          </div>
        </Link>
      </div>

      <nav className="flex-1 p-3 space-y-1">
        {nav.map((item) => {
          const active = path === item.href || (item.href !== "/" && path.startsWith(item.href));
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-all duration-150",
                active
                  ? "bg-accent/10 text-accent font-medium"
                  : "text-muted hover:text-foreground hover:bg-card"
              )}
            >
              <span className="text-base w-5 text-center">{item.icon}</span>
              {item.label}
            </Link>
          );
        })}
      </nav>

      <div className="p-4 border-t border-border">
        <div className="flex items-center gap-2 text-xs text-muted">
          <span className="w-2 h-2 rounded-full bg-success" />
          System Online
        </div>
      </div>
    </aside>
  );
}
