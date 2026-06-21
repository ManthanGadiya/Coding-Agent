"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";

export default function Projects() {
  const [projects, setProjects] = useState<any[]>([]);

  useEffect(() => {
    api.projects.list().then((d: any) => setProjects(d.projects ?? d)).catch(() => {});
  }, []);

  return (
    <div className="space-y-6 animate-in">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold tracking-tight">Projects</h1>
        <button className="px-3 py-1.5 bg-accent text-black rounded-lg text-sm font-medium hover:bg-accent-dim transition-colors">+ New</button>
      </div>
      <div className="grid gap-3">
        {projects.length === 0 && <p className="text-muted text-sm">No projects yet.</p>}
        {projects.map((p) => (
          <div key={p.id} className="bg-card border border-border rounded-xl p-5 flex items-center justify-between">
            <div>
              <div className="font-semibold">{p.display_name}</div>
              <div className="text-sm text-muted mt-0.5">{p.task_count} tasks · {p.completed_task_count} completed</div>
            </div>
            <div className="flex items-center gap-4">
              <div className="text-xs text-muted font-mono">{p.created_at?.slice(0, 10)}</div>
              <span className={`px-2.5 py-1 rounded-full text-xs font-mono font-medium ${
                p.status === "active" ? "bg-success/10 text-success" : "bg-muted/10 text-muted"
              }`}>{p.status}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
