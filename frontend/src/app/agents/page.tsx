"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";

const icons: Record<string, string> = {
  "manager": "⧉", "coder": "⊡", "reviewer": "⊟",
  "tester": "⊠", "memory": "⊞", "debugger": "⊡",
  "architect": "⌗", "planner": "⌘",
};

export default function Agents() {
  const [agents, setAgents] = useState<any[]>([]);

  useEffect(() => {
    api.manager.status().then((d: any) => {
      const list = Object.entries(d.agents ?? {}).map(([id, a]: any) => ({
        id, name: id.replace("-1", "").replace(/^\w/, (c: string) => c.toUpperCase()),
        type: (a.capabilities ?? [])[0] ?? "general",
        status: a.state ?? "idle",
        tasks: (a.tasks_completed ?? 0) + (a.tasks_failed ?? 0),
        icon: icons[id.replace("-1", "")] ?? "●",
        capabilities: a.capabilities ?? [],
      }));
      setAgents(list);
    }).catch(() => {});
  }, []);

  return (
    <div className="space-y-6 animate-in">
      <h1 className="text-2xl font-bold tracking-tight">Agents</h1>
      <p className="text-sm text-muted">{agents.length} registered agents</p>
      <div className="grid grid-cols-3 gap-4">
        {agents.map((a) => (
          <Link key={a.id} href={`/agents/${a.id}`} className="bg-card border border-border rounded-xl p-5 hover:bg-card-hover transition-colors block">
            <div className="flex items-center justify-between mb-3">
              <div className="w-10 h-10 rounded-lg bg-accent/10 flex items-center justify-center text-accent text-lg">{a.icon}</div>
              <span className={`px-2 py-0.5 rounded-full text-xs font-mono ${
                a.status === "busy" || a.status === "executing" ? "bg-accent/10 text-accent" : "bg-success/10 text-success"
              }`}>{a.status}</span>
            </div>
            <div className="font-semibold">{a.name}</div>
            <div className="text-xs text-muted mt-0.5">{a.type}</div>
            <div className="text-xs text-muted mt-2 font-mono">{a.tasks} tasks · {a.capabilities.slice(0, 3).join(", ")}</div>
          </Link>
        ))}
      </div>
    </div>
  );
}
