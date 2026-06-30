"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";

export default function Dashboard() {
  const [data, setData] = useState<{ orch: any; projects: any[]; tasks: any[]; mem: any }>({ orch: null, projects: [], tasks: [], mem: null });
  const [form, setForm] = useState({ goal: "", running: false, result: null as any });

  useEffect(() => {
    api.manager.status().then((d) => setData(s => ({...s, orch: d}))).catch(() => {});
    api.projects.list().then((d: any) => setData(s => ({...s, projects: d.projects ?? d}))).catch(() => {});
    api.tasks.list().then((d: any) => setData(s => ({...s, tasks: d.tasks ?? d}))).catch(() => {});
    api.memory.stats().then((d) => setData(s => ({...s, mem: d}))).catch(() => {});
  }, []);

  async function runGoal() {
    if (!form.goal.trim()) return;
    setForm(f => ({...f, running: true, result: null}));
    try {
      const res = await api.agents.runGoal(form.goal.trim());
      setForm(f => ({...f, result: res}));
    } catch (e: any) {
      setForm(f => ({...f, result: { success: false, error: e.message } }));
    } finally {
      setForm(f => ({...f, running: false}));
    }
  }

  const stats = [
    { label: "Agents", value: data.orch?.registered_agents ?? "-", sub: `${data.orch?.agents ? Object.values(data.orch.agents).filter((a: any) => a.state === "idle").length : "-"} idle` },
    { label: "Projects", value: data.projects.length, sub: `${data.projects.filter((p: any) => p.status === "active").length} active` },
    { label: "Tasks", value: data.tasks.length, sub: `${data.tasks.filter((t: any) => t.status !== "completed").length} pending` },
    { label: "Memory", value: data.mem?.total ?? data.mem?.entries ?? "-", sub: `${data.mem?.global ?? 0} global · ${data.mem?.project ?? 0} project` },
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
          <input aria-label="Goal description"
            className="flex-1 bg-surface border border-border rounded-lg px-4 py-2.5 text-sm outline-none focus:border-accent transition-colors"
            placeholder="Describe what you want CAMera to do..."
            value={form.goal}
            onChange={(e) => setForm(f => ({...f, goal: e.target.value}))}
            onKeyDown={(e) => e.key === "Enter" && runGoal()}
          />
          <button type="button"
            onClick={runGoal}
            disabled={form.running || !form.goal.trim()}
            className="px-5 py-2.5 bg-accent text-black font-medium rounded-lg text-sm hover:brightness-110 disabled:opacity-40 transition-all"
          >
            {form.running ? "Running..." : "Run"}
          </button>
        </div>

        {form.result && (
          <div className="mt-4 space-y-2">
            <div className="flex items-center gap-3 text-sm">
              <span className="text-muted">Classification:</span>
              <span className="font-mono text-accent">{form.result.classification}</span>
              <span className="text-muted">Complexity:</span>
              <span className="font-mono text-accent">{form.result.complexity}</span>
              <span className="text-muted">Pipeline:</span>
              <span className="font-mono text-accent">{form.result.pipeline_id}</span>
              <span className={`px-2 py-0.5 rounded-full text-xs font-mono ${
                form.result.success ? "bg-success/10 text-success" : "bg-error/10 text-error"
              }`}>{form.result.success ? "Success" : "Failed"}</span>
            </div>
            <div className="text-xs text-muted">
              {form.result.completed_steps}/{form.result.total_steps} steps completed
            </div>
            <div className="space-y-1 max-h-48 overflow-y-auto">
              {(form.result.steps ?? []).map((s: any, i: number) => (
                <div key={s.step} className="flex items-center gap-3 text-xs font-mono bg-surface rounded-lg px-3 py-2">
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

      {data.orch?.agents && (
        <div className="animate-in">
          <h2 className="text-lg font-semibold mb-3">Agents</h2>
          <div className="grid grid-cols-3 gap-3">
              {Object.entries(data.orch.agents).map(([id, a]: any) => (
                <Link key={id} href={`/agents/${id}`} className="bg-card border border-border rounded-xl p-4 flex items-center justify-between hover:bg-card-hover transition-colors">
                <div>
                  <div className="text-sm font-medium">{id.replace("-1", "")}</div>
                  <div className="text-xs text-muted mt-0.5 font-mono">{a.capabilities.slice(0, 3).join(", ")}</div>
                </div>
                 <span className={`px-2 py-0.5 rounded-full text-xs font-mono ${
                   a.state === "idle" ? "bg-success/10 text-success" : "bg-accent/10 text-accent"
                 }`}>{a.state}</span>
               </Link>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
