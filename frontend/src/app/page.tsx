"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";

export default function Dashboard() {
  const [orch, setOrch] = useState<any>(null);
  const [projects, setProjects] = useState<any[]>([]);
  const [tasks, setTasks] = useState<any[]>([]);

  useEffect(() => {
    api.orchestrator.status().then(setOrch).catch(() => {});
    api.projects.list().then(setProjects).catch(() => {});
    api.tasks.list().then(setTasks).catch(() => {});
  }, []);

  const stats = [
    { label: "Agents", value: orch?.registered_agents ?? "-", sub: `${orch?.agents ? Object.values(orch.agents).filter((a: any) => a.state === "idle").length : "-"} idle` },
    { label: "Projects", value: projects.length, sub: `${projects.filter((p: any) => p.status === "active").length} active` },
    { label: "Tasks", value: tasks.length, sub: `${tasks.filter((t: any) => t.status !== "completed").length} pending` },
    { label: "Memory", value: "?", sub: "click Memory tab" },
  ];

  return (
    <div className="space-y-8">
      <div className="animate-in">
        <h1 className="text-2xl font-bold tracking-tight">Dashboard</h1>
        <p className="text-muted text-sm mt-1">System overview</p>
      </div>

      <div className="grid grid-cols-4 gap-4 animate-in">
        {stats.map((s) => (
          <div key={s.label} className="bg-card border border-border rounded-xl p-5">
            <div className="text-2xl font-mono font-bold text-accent">{s.value}</div>
            <div className="text-sm font-medium mt-1">{s.label}</div>
            <div className="text-xs text-muted mt-0.5">{s.sub}</div>
          </div>
        ))}
      </div>

      {orch?.agents && (
        <div className="animate-in">
          <h2 className="text-lg font-semibold mb-3">Agents</h2>
          <div className="grid grid-cols-3 gap-3">
            {Object.entries(orch.agents).map(([id, a]: any) => (
              <div key={id} className="bg-card border border-border rounded-xl p-4 flex items-center justify-between">
                <div>
                  <div className="text-sm font-medium">{id.replace("-1", "")}</div>
                  <div className="text-xs text-muted mt-0.5 font-mono">{a.capabilities.slice(0, 3).join(", ")}</div>
                </div>
                <span className={`px-2 py-0.5 rounded-full text-xs font-mono ${
                  a.state === "idle" ? "bg-success/10 text-success" : "bg-accent/10 text-accent"
                }`}>{a.state}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
