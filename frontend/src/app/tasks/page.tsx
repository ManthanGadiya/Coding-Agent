"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";

const badge = (s: string) => {
  const m: Record<string, string> = {
    pending: "bg-muted/10 text-muted",
    in_progress: "bg-accent/10 text-accent",
    completed: "bg-success/10 text-success",
    failed: "bg-error/10 text-error",
    cancelled: "bg-muted/10 text-muted",
    blocked: "bg-error/10 text-error",
  };
  return m[s] || "bg-muted/10 text-muted";
};

const typeBadge = (t: string) => {
  const m: Record<string, string> = {
    feature: "text-blue-400",
    bugfix: "text-error",
    refactor: "text-purple-400",
    research: "text-cyan-400",
    implementation: "text-accent",
    testing: "text-green-400",
    review: "text-pink-400",
    documentation: "text-muted",
  };
  return m[t] || "text-muted";
};

export default function Tasks() {
  const [tasks, setTasks] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState("");
  const [showCreate, setShowCreate] = useState(false);
  const [title, setTitle] = useState("");
  const [desc, setDesc] = useState("");
  const [type, setType] = useState("feature");

  useEffect(() => { loadTasks(); }, [filter]);

  async function loadTasks() {
    setLoading(true);
    try {
      const params = filter ? `status=${filter}` : "";
      const d: any = await api.tasks.list(params);
      setTasks(Array.isArray(d) ? d : d.tasks ?? []);
    } catch { setTasks([]); }
    finally { setLoading(false); }
  }

  async function toggleStatus(t: any) {
    const newStatus = t.status === "completed" ? "pending" : "completed";
    await api.tasks.update(t.id, { status: newStatus }).catch(() => {});
    loadTasks();
  }

  async function createTask() {
    if (!title.trim()) return;
    await api.tasks.create({ title: title.trim(), description: desc || undefined, task_type: type });
    setTitle(""); setDesc(""); setShowCreate(false);
    loadTasks();
  }

  return (
    <div className="space-y-6 animate-in">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold tracking-tight">Tasks</h1>
        <button onClick={() => setShowCreate(!showCreate)}
          className="px-4 py-2 bg-accent text-black font-medium rounded-lg text-sm hover:brightness-110 transition-all">
          {showCreate ? "Cancel" : "+ New Task"}
        </button>
      </div>

      {showCreate && (
        <div className="bg-card border border-border rounded-xl p-5 space-y-3">
          <input className="w-full bg-surface border border-border rounded-lg px-4 py-2.5 text-sm outline-none focus:border-accent"
            placeholder="Task title" value={title} onChange={(e) => setTitle(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && createTask()} />
          <input className="w-full bg-surface border border-border rounded-lg px-4 py-2.5 text-sm outline-none focus:border-accent"
            placeholder="Description (optional)" value={desc} onChange={(e) => setDesc(e.target.value)} />
          <div className="flex gap-2 items-center">
            <select className="bg-surface border border-border rounded-lg px-3 py-2 text-sm outline-none"
              value={type} onChange={(e) => setType(e.target.value)}>
              {["feature", "bugfix", "refactor", "research", "implementation", "testing", "review", "documentation"].map(t =>
                <option key={t} value={t}>{t}</option>
              )}
            </select>
            <button onClick={createTask} disabled={!title.trim()}
              className="px-4 py-2 bg-accent text-black font-medium rounded-lg text-sm disabled:opacity-40">
              Create
            </button>
          </div>
        </div>
      )}

      <div className="flex gap-2 flex-wrap">
        {["", "pending", "in_progress", "completed", "failed"].map((s) => (
          <button key={s} type="button" onClick={() => setFilter(s)}
            className={`px-3 py-1.5 rounded-lg text-xs font-mono transition-colors ${
              filter === s ? "bg-accent text-black" : "bg-card border border-border text-muted hover:text-foreground"
            }`}>{s || "all"}</button>
        ))}
      </div>

      {loading ? (
        <div className="text-center text-muted text-sm py-12">Loading...</div>
      ) : tasks.length === 0 ? (
        <div className="text-center text-muted text-sm py-12">No tasks found</div>
      ) : (
        <div className="bg-card border border-border rounded-xl divide-y divide-border">
          {tasks.map((t: any) => (
            <div key={t.id} className="flex items-center gap-4 px-5 py-4">
              <input type="checkbox" checked={t.status === "completed"} onChange={() => toggleStatus(t)}
                aria-label={`Mark "${t.title}" as complete`} className="accent-accent rounded cursor-pointer" />
              <div className="flex-1 min-w-0">
                <div className={`text-sm font-medium truncate ${t.status === "completed" ? "line-through text-muted" : ""}`}>
                  {t.title}
                </div>
                <div className="text-xs text-muted truncate">{t.description || t.id}</div>
              </div>
              <span className={`text-[10px] font-mono ${typeBadge(t.task_type)}`}>{t.task_type}</span>
              {t.assigned_agent && <span className="text-xs text-muted font-mono">{t.assigned_agent}</span>}
              <span className={`px-2 py-0.5 rounded-full text-[10px] font-mono ${badge(t.status)}`}>
                {t.status.replace("_", " ")}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
