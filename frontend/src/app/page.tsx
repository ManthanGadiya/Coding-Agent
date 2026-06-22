"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";

export default function Dashboard() {
  const [orch, setOrch] = useState<any>(null);
  const [projects, setProjects] = useState<any[]>([]);
  const [tasks, setTasks] = useState<any[]>([]);
  const [goal, setGoal] = useState("");
  const [running, setRunning] = useState(false);
  const [result, setResult] = useState<any>(null);

  useEffect(() => {
    api.manager.status().then(setOrch).catch(() => {});
    api.projects.list().then((d: any) => setProjects(d.projects ?? d)).catch(() => {});
    api.tasks.list().then((d: any) => setTasks(d.tasks ?? d)).catch(() => {});
  }, []);

  async function runGoal() {
    if (!goal.trim()) return;
    setRunning(true);
    setResult(null);
    try {
      const res = await api.agents.runGoal(goal.trim());
      setResult(res);
    } catch (e: any) {
      setResult({ success: false, error: e.message });
    } finally {
      setRunning(false);
    }
  }

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

      <div className="bg-card border border-border rounded-xl p-5 animate-in">
        <h2 className="text-sm font-semibold mb-3">Run Goal</h2>
        <div className="flex gap-3">
          <input
            className="flex-1 bg-surface border border-border rounded-lg px-4 py-2.5 text-sm outline-none focus:border-accent transition-colors"
            placeholder="Describe what you want CAMera to do..."
            value={goal}
            onChange={(e) => setGoal(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && runGoal()}
          />
          <button
            onClick={runGoal}
            disabled={running || !goal.trim()}
            className="px-5 py-2.5 bg-accent text-black font-medium rounded-lg text-sm hover:brightness-110 disabled:opacity-40 transition-all"
          >
            {running ? "Running..." : "Run"}
          </button>
        </div>

        {result && (
          <div className="mt-4 space-y-2">
            <div className="flex items-center gap-3 text-sm">
              <span className="text-muted">Classification:</span>
              <span className="font-mono text-accent">{result.classification}</span>
              <span className="text-muted">Complexity:</span>
              <span className="font-mono text-accent">{result.complexity}</span>
              <span className="text-muted">Pipeline:</span>
              <span className="font-mono text-accent">{result.pipeline_id}</span>
              <span className={`px-2 py-0.5 rounded-full text-xs font-mono ${
                result.success ? "bg-success/10 text-success" : "bg-error/10 text-error"
              }`}>{result.success ? "Success" : "Failed"}</span>
            </div>
            <div className="text-xs text-muted">
              {result.completed_steps}/{result.total_steps} steps completed
            </div>
            <div className="space-y-1 max-h-48 overflow-y-auto">
              {(result.steps ?? []).map((s: any, i: number) => (
                <div key={i} className="flex items-center gap-3 text-xs font-mono bg-surface rounded-lg px-3 py-2">
                  <span className={`w-2 h-2 rounded-full ${s.status === "completed" ? "bg-success" : "bg-error"}`} />
                  <span className="text-muted w-24 truncate">{s.step}</span>
                  <span className="text-muted w-20">{s.agent}</span>
                  <span className="flex-1 truncate text-muted">{s.error || s.output?.slice(0, 80) || ""}</span>
                </div>
              ))}
            </div>
          </div>
        )}
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
