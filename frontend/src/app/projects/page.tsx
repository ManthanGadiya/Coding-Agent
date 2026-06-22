"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";

export default function Projects() {
  const [projects, setProjects] = useState<any[]>([]);
  const [showCreate, setShowCreate] = useState(false);
  const [name, setName] = useState("");
  const [desc, setDesc] = useState("");

  useEffect(() => {
    api.projects.list().then((d: any) => setProjects(d.projects ?? d)).catch(() => {});
  }, []);

  async function createProject() {
    if (!name.trim()) return;
    await api.projects.create({ name: name.trim(), display_name: name.trim(), description: desc || undefined }).catch(() => {});
    setName(""); setDesc(""); setShowCreate(false);
    api.projects.list().then((d: any) => setProjects(d.projects ?? d)).catch(() => {});
  }

  return (
    <div className="space-y-6 animate-in">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold tracking-tight">Projects</h1>
        <button type="button" onClick={() => setShowCreate(!showCreate)}
          className="px-3 py-1.5 bg-accent text-black rounded-lg text-sm font-medium hover:bg-accent-dim transition-colors">
          {showCreate ? "Cancel" : "+ New"}
        </button>
      </div>

      {showCreate && (
        <div className="bg-card border border-border rounded-xl p-5 space-y-3">
          <input className="w-full bg-surface border border-border rounded-lg px-4 py-2.5 text-sm outline-none focus:border-accent"
            placeholder="Project name" value={name} onChange={(e) => setName(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && createProject()} />
          <input className="w-full bg-surface border border-border rounded-lg px-4 py-2.5 text-sm outline-none focus:border-accent"
            placeholder="Description (optional)" value={desc} onChange={(e) => setDesc(e.target.value)} />
          <button onClick={createProject} disabled={!name.trim()}
            className="px-4 py-2 bg-accent text-black font-medium rounded-lg text-sm disabled:opacity-40">Create</button>
        </div>
      )}
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
