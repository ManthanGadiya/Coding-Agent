"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import type { AgentInfo, ManagerStatusResponse, Project, TaskResponse } from "@/lib/api";

import { Skeleton } from "@/components/ui";

type OrchStatus = ManagerStatusResponse & { registered_agents?: number; agents?: Record<string, AgentInfo> };
type MemStats = { total?: number; entries?: number; global?: number; project?: number };
type ProjectsPayload = { projects?: Project[] } | Project[];
type TasksPayload = { tasks?: TaskResponse[] } | TaskResponse[];
type RunGoalResult = {
  success?: boolean;
  classification?: string;
  complexity?: string;
  pipeline_id?: string;
  completed_steps?: number;
  total_steps?: number;
  steps?: Array<{ step?: string; status?: string; agent?: string; error?: string; output?: string }>;
};

export default function Dashboard() {
  const [data, setData] = useState<{ orch: OrchStatus | null; projects: Project[]; tasks: TaskResponse[]; mem: MemStats | null }>({ orch: null, projects: [], tasks: [], mem: null });
  const [form, setForm] = useState({ goal: "", running: false, result: null as RunGoalResult | null });
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    Promise.all([
      api.manager.status().then((d) => setData(s => ({...s, orch: d}))).catch(() => {}),
      api.projects.list().then((d) => { const p = d as ProjectsPayload; setData(s => ({...s, projects: Array.isArray(p) ? p : p.projects ?? []})); }).catch(() => {}),
      api.tasks.list().then((d) => { const t = d as TasksPayload; setData(s => ({...s, tasks: Array.isArray(t) ? t : t.tasks ?? []})); }).catch(() => {}),
      api.memory.stats().then((d) => setData(s => ({...s, mem: d}))).catch(() => {}),
    ]).finally(() => setLoaded(true));
  }, []);

  async function runGoal() {
    if (!form.goal.trim()) return;
    setForm(f => ({...f, running: true, result: null}));
    try {
      const res = await api.agents.runGoal(form.goal.trim());
      setForm(f => ({...f, result: res as RunGoalResult}));
    } catch (e) {
      setForm(f => ({...f, result: { success: false, error: e instanceof Error ? e.message : String(e) } }));
    } finally {
      setForm(f => ({...f, running: false}));
    }
  }

  const stats = [
    { label: "Agents", value: data.orch?.registered_agents ?? "-", sub: `${data.orch?.agents ? Object.values(data.orch.agents).filter((a) => a.state === "idle").length : "-"} idle` },
    { label: "Projects", value: data.projects.length, sub: `${data.projects.filter((p) => p.status === "active").length} active` },
    { label: "Tasks", value: data.tasks.length, sub: `${data.tasks.filter((t) => t.status !== "completed").length} pending` },
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
              {(form.result.steps ?? []).map((s) => (
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
          {!loaded ? Array.from({length: 4}).map((_, i) => (
            <div key={i} className="bg-card border border-border rounded-xl p-5 space-y-2">
              <Skeleton className="h-7 w-16" />
              <Skeleton className="h-4 w-20" />
              <Skeleton className="h-3 w-28" />
            </div>
          )) : stats.map((s) => (
            <div key={s.label} className="bg-card border border-border rounded-xl p-5">
              <div className="text-2xl font-mono font-bold text-accent">{s.value}</div>
              <div className="text-sm font-medium mt-1">{s.label}</div>
              <div className="text-xs text-muted mt-0.5">{s.sub}</div>
            </div>
          ))}
        </div>

      {data.tasks.length > 0 && (
        <div className="grid grid-cols-2 gap-4 animate-in">
          <div className="bg-card border border-border rounded-xl p-5">
            <h2 className="text-sm font-semibold mb-3">Task Status</h2>
            <ChartBar label="Completed" count={data.tasks.filter((t) => t.status === "completed").length} total={data.tasks.length} color="bg-success" />
            <ChartBar label="In Progress" count={data.tasks.filter((t) => t.status === "in_progress").length} total={data.tasks.length} color="bg-accent" />
            <ChartBar label="Pending" count={data.tasks.filter((t) => t.status === "pending" || t.status === "open").length} total={data.tasks.length} color="bg-yellow-500" />
            <ChartBar label="Failed" count={data.tasks.filter((t) => t.status === "failed").length} total={data.tasks.length} color="bg-red-500" />
          </div>
          {data.orch?.agents && (
            <div className="bg-card border border-border rounded-xl p-5">
              <h2 className="text-sm font-semibold mb-3">Agent Performance</h2>
              {Object.entries(data.orch.agents).map(([id, a]) => {
                const total = (a.tasks_completed || 0) + (a.tasks_failed || 0);
                return (
                  <div key={id} className="mb-3">
                    <div className="flex justify-between text-xs mb-1">
                      <span className="font-mono">{id.replace("-1", "")}</span>
                      <span className="text-muted">{a.tasks_completed ?? 0}/{total} ({total ? Math.round((a.tasks_completed || 0) / total * 100) : 0}%)</span>
                    </div>
                    <div className="h-2 bg-surface rounded-full overflow-hidden">
                      {total > 0 && <div className="h-full bg-success rounded-full transition-all" style={{ width: `${((a.tasks_completed || 0) / total) * 100}%` }} />}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}

      {data.orch?.agents && (
        <div className="animate-in">
          <h2 className="text-lg font-semibold mb-3">Agents</h2>
          <div className="grid grid-cols-3 gap-3">
              {Object.entries(data.orch.agents).map(([id, a]) => (
                <Link key={id} href={`/agents/${id}`} className="bg-card border border-border rounded-xl p-4 flex items-center justify-between hover:bg-card-hover transition-colors">
                <div>
                  <div className="text-sm font-medium">{id.replace("-1", "")}</div>
                  <div className="text-xs text-muted mt-0.5 font-mono">{(a.capabilities ?? []).slice(0, 3).join(", ")}</div>
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

function ChartBar({ label, count, total, color }: { label: string; count: number; total: number; color: string }) {
  const pct = total > 0 ? (count / total) * 100 : 0;
  return (
    <div className="mb-2">
      <div className="flex justify-between text-xs mb-1">
        <span>{label}</span>
        <span className="text-muted">{count}</span>
      </div>
      <div className="h-2 bg-surface rounded-full overflow-hidden">
        <div className={`h-full rounded-full transition-all ${color}`} style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
}
