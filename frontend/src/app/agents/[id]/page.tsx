"use client";

import { useEffect, useState } from "react";
import { use } from "react";
import Link from "next/link";
import { api } from "@/lib/api";

const icons: Record<string, string> = {
  "manager": "⧉", "coder": "⊡", "reviewer": "⊟",
  "tester": "⊠", "memory": "⊞", "debugger": "⊡",
  "architect": "⌗", "planner": "⌘",
};

export default function AgentDetail({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const [data, setData] = useState<{ agent: any; runtime: any; profile: any; tasks: any[]; loading: boolean }>({ agent: null, runtime: null, profile: null, tasks: [], loading: true });

  useEffect(() => {
    Promise.all([
      api.agents.get(id).catch(() => null),
      api.agents.status(id).catch(() => null),
      api.memoryRetrieval.profile(id.replace("-1", "")).catch(() => null),
      api.tasks.list(`assigned_agent=${id}`).then((d: any) => Array.isArray(d) ? d : d.tasks ?? []).catch(() => []),
    ]).then(([a, r, p, t]) => {
      setData({ agent: a, runtime: r, profile: p, tasks: t, loading: false });
    });
  }, [id]);

  if (data.loading) return <div className="text-center text-muted text-sm py-24">Loading...</div>;
  if (!data.agent && !data.runtime) return <div className="text-center text-muted text-sm py-24">Agent not found</div>;

  const typeKey = (data.agent?.agent_type ?? data.runtime?.agent_id ?? id).replace("-1", "").replace(/_\d+$/, "");
  const icon = icons[typeKey] ?? "●";
  const name = data.agent?.name ?? data.runtime?.name ?? typeKey.replace(/^\w/, (c: string) => c.toUpperCase());
  const state = data.runtime?.state ?? data.agent?.status ?? "unknown";
  const caps = data.runtime?.capabilities ?? data.agent?.capabilities ?? [];

  return (
    <div className="space-y-6 animate-in">
      <Link href="/agents" className="text-sm text-muted hover:text-foreground transition-colors">&larr; Back to Agents</Link>

      <div className="bg-card border border-border rounded-xl p-6">
        <div className="flex items-start gap-5">
          <div className="w-14 h-14 rounded-xl bg-accent/10 flex items-center justify-center text-accent text-2xl">{icon}</div>
          <div className="flex-1">
            <div className="flex items-center gap-3">
              <h1 className="text-2xl font-bold">{name}</h1>
              <span className={`px-2.5 py-1 rounded-full text-xs font-mono ${
                state === "idle" ? "bg-success/10 text-success" : state === "busy" || state === "executing" ? "bg-accent/10 text-accent" : "bg-error/10 text-error"
              }`}>{state}</span>
            </div>
            <div className="text-sm text-muted mt-1 font-mono">{data.agent?.agent_type ?? typeKey}</div>
            {data.agent?.description && <div className="text-sm text-muted mt-2">{data.agent.description}</div>}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-4">
        <div className="bg-card border border-border rounded-xl p-5">
          <div className="text-2xl font-mono font-bold text-accent">{data.runtime?.tasks_completed ?? data.agent?.tasks_completed ?? 0}</div>
          <div className="text-sm font-medium mt-1">Completed</div>
        </div>
        <div className="bg-card border border-border rounded-xl p-5">
          <div className="text-2xl font-mono font-bold text-error">{data.runtime?.tasks_failed ?? data.agent?.tasks_failed ?? 0}</div>
          <div className="text-sm font-medium mt-1">Failed</div>
        </div>
        <div className="bg-card border border-border rounded-xl p-5">
          <div className="text-2xl font-mono font-bold text-accent">{data.tasks.length}</div>
          <div className="text-sm font-medium mt-1">Active Tasks</div>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-6">
        <div className="bg-card border border-border rounded-xl p-5">
          <h2 className="text-sm font-semibold mb-3">Capabilities</h2>
          {caps.length === 0 ? (
            <p className="text-xs text-muted">No capabilities registered</p>
          ) : (
            <div className="flex flex-wrap gap-2">
              {caps.map((c: string) => (
                <span key={c} className="px-2.5 py-1 rounded-full text-xs font-mono bg-accent/10 text-accent">{c}</span>
              ))}
            </div>
          )}
        </div>

        <div className="bg-card border border-border rounded-xl p-5">
          <h2 className="text-sm font-semibold mb-3">Permissions</h2>
          {(data.agent?.permissions ?? []).length === 0 ? (
            <p className="text-xs text-muted">No permissions configured</p>
          ) : (
            <div className="flex flex-wrap gap-2">
              {(data.agent?.permissions ?? []).map((p: string) => (
                <span key={p} className="px-2.5 py-1 rounded-full text-xs font-mono bg-surface text-muted border border-border">{p}</span>
              ))}
            </div>
          )}
        </div>
      </div>

      {data.profile && (
        <div className="bg-card border border-border rounded-xl p-5">
          <h2 className="text-sm font-semibold mb-3">Memory Profile</h2>
          <div className="grid grid-cols-2 gap-4 text-sm">
            {data.profile.architecture_decisions && (
              <div>
                <div className="text-muted text-xs mb-1">Architecture Decisions</div>
                <div className="text-lg font-mono font-bold text-accent">{data.profile.architecture_decisions}</div>
              </div>
            )}
            {data.profile.known_patterns && (
              <div>
                <div className="text-muted text-xs mb-1">Known Patterns</div>
                <div className="text-lg font-mono font-bold text-accent">{data.profile.known_patterns}</div>
              </div>
            )}
            {data.profile.interaction_count && (
              <div>
                <div className="text-muted text-xs mb-1">Interactions</div>
                <div className="text-lg font-mono font-bold text-accent">{data.profile.interaction_count}</div>
              </div>
            )}
            {data.profile.last_active && (
              <div>
                <div className="text-muted text-xs mb-1">Last Active</div>
                <div className="text-lg font-mono font-bold text-accent">{data.profile.last_active?.slice(0, 10)}</div>
              </div>
            )}
          </div>
        </div>
      )}

      {data.tasks.length > 0 && (
        <div className="bg-card border border-border rounded-xl">
          <div className="px-5 py-4 border-b border-border">
            <h2 className="text-sm font-semibold">Tasks</h2>
          </div>
          <div className="divide-y divide-border">
            {data.tasks.map((t: any) => (
              <div key={t.id} className="flex items-center gap-4 px-5 py-3.5">
                <div className="flex-1 min-w-0">
                  <div className="text-sm font-medium truncate">{t.title}</div>
                  <div className="text-xs text-muted truncate">{t.description || t.id}</div>
                </div>
                <span className="text-xs text-muted font-mono">{t.task_type}</span>
                <span className={`px-2 py-0.5 rounded-full text-[10px] font-mono ${
                  t.status === "completed" ? "bg-success/10 text-success" : t.status === "in_progress" ? "bg-accent/10 text-accent" : t.status === "failed" ? "bg-error/10 text-error" : "bg-muted/10 text-muted"
                }`}>{t.status.replace("_", " ")}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
