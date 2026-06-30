"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import { CardSkeleton, ListSkeleton } from "@/components/ui";

const icons: Record<string, string> = {
  manager: "⧉", coder: "⊡", reviewer: "⊟", tester: "⊠",
  memory: "⊞", debugger: "⊡", architect: "⌗", planner: "⌘",
};

export default function AgentsPage() {
  const [agents, setAgents] = useState<any[]>([]);
  const [loaded, setLoaded] = useState(false);
  const [tab, setTab] = useState<"agents" | "registry" | "conflicts" | "disagreements">("agents");
  const [registry, setRegistry] = useState<any[]>([]);
  const [conflicts, setConflicts] = useState<any[]>([]);
  const [disagreements, setDisagreements] = useState<any[]>([]);
  const [resInput, setResInput] = useState<Record<string, string>>({});

  useEffect(() => {
    api.manager.status().then((d: any) => {
      const list = Object.entries(d.agents ?? {}).map(([id, a]: any) => ({
        id, name: id.replace("-1", "").replace(/^\w/, (c: string) => c.toUpperCase()),
        type: (a.capabilities ?? [])[0] ?? "general", status: a.state ?? "idle",
        tasks: (a.tasks_completed ?? 0) + (a.tasks_failed ?? 0),
        icon: icons[id.replace("-1", "")] ?? "●", capabilities: a.capabilities ?? [],
      }));
      setAgents(list);
    }).catch(() => {}).finally(() => setLoaded(true));
  }, []);

  function loadRegistry() {
    api.agents.registry().then(setRegistry).catch(() => {});
    api.agents.conflictHistory().then(setConflicts).catch(() => {});
    api.agents.disagreementUnresolved().then((d) => setDisagreements(d as any[])).catch(() => {});
  }

  function resolveConflict(data: Record<string, unknown>) {
    api.agents.conflictResolve(data).then(() => api.agents.conflictHistory().then(setConflicts)).catch(() => {});
  }

  function resolveDisagreement(id: string) {
    const resolution = resInput[id] || "auto-resolved";
    api.agents.disagreementResolve(id, resolution).then(() => {
      api.agents.disagreementUnresolved().then((d) => setDisagreements(d as any[])).catch(() => {});
      setResInput(r => { const n = {...r}; delete n[id]; return n; });
    }).catch(() => {});
  }

  return (
    <div className="space-y-8">
      <div className="animate-in">
        <h1 className="text-2xl font-bold tracking-tight">Agents</h1>
        <p className="text-muted text-sm mt-1">{agents.length} registered agents</p>
      </div>

      <div className="flex gap-2 border-b border-border pb-2 animate-in">
        {(["agents", "registry", "conflicts", "disagreements"] as const).map(t => (
          <button key={t} type="button" onClick={() => { setTab(t); if (t !== "agents") loadRegistry(); }}
            className={`px-4 py-2 rounded-lg text-sm font-medium capitalize ${tab === t ? "bg-accent/10 text-accent" : "text-muted hover:text-foreground"}`}>{t}</button>
        ))}
      </div>

      {tab === "agents" && (
        <div className="grid grid-cols-3 gap-4 animate-in">
          {!loaded ? Array.from({length: 3}).map((_, i) => <CardSkeleton key={i} />) : agents.length === 0 ? (
            <p className="text-sm text-muted col-span-3 text-center py-12">No agents found. Start the agent manager to see agents here.</p>
          ) : agents.map((a) => (
            <Link key={a.id} href={`/agents/${a.id}`} className="bg-card border border-border rounded-xl p-5 hover:border-accent/30 transition-colors block">
              <div className="flex items-center justify-between mb-3">
                <div className="w-10 h-10 rounded-lg bg-accent/10 flex items-center justify-center text-accent text-lg">{a.icon}</div>
                <span className={`px-2 py-0.5 rounded-full text-xs font-mono ${a.status === "busy" || a.status === "executing" ? "bg-accent/10 text-accent" : "bg-success/10 text-success"}`}>{a.status}</span>
              </div>
              <div className="font-semibold">{a.name}</div>
              <div className="text-xs text-muted mt-0.5">{a.type}</div>
              <div className="text-xs text-muted mt-2 font-mono">{a.tasks} tasks · {a.capabilities.slice(0, 3).join(", ")}</div>
            </Link>
          ))}
        </div>
      )}

      {tab === "registry" && (
        <div className="space-y-3 animate-in">
          {registry.length === 0 ? <p className="text-sm text-muted py-8 text-center">No registry entries. Run the agent manager to populate the registry.</p> : (
            <div className="bg-card border border-border rounded-xl divide-y divide-border">
              {registry.map((r: any) => (
                <div key={r.agent_id || r.id} className="px-5 py-4">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-mono text-accent">{r.agent_id || r.name}</span>
                    <span className="text-[10px] text-muted font-mono">{r.type || r.agent_type}</span>
                  </div>
                  {r.capabilities?.length > 0 && (
                    <div className="flex gap-1 mt-2 flex-wrap">
                      {(r.capabilities || []).slice(0, 5).map((c: string) => (
                        <span key={c} className="text-[10px] bg-surface rounded px-1.5 py-0.5 font-mono text-muted">{c}</span>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {tab === "conflicts" && (
        <div className="space-y-3 animate-in">
          {conflicts.length === 0 ? <p className="text-sm text-muted">No conflict history.</p> : (
            <div className="bg-card border border-border rounded-xl divide-y divide-border">
              {conflicts.map((c: any) => (
                <div key={c.conflict_id || c.id} className="px-5 py-4">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-xs font-mono text-muted">{c.conflict_id || c.id}</span>
                    <span className={`px-2 py-0.5 rounded text-xs font-mono ${c.resolved ? "bg-success/10 text-success" : "bg-yellow-500/10 text-yellow-500"}`}>{c.resolved ? "Resolved" : "Open"}</span>
                  </div>
                  <p className="text-sm">{c.description || c.details}</p>
                  {!c.resolved && (
                    <button type="button" onClick={() => resolveConflict({ conflict_id: c.conflict_id || c.id })}
                      className="mt-2 px-3 py-1 text-xs bg-accent/10 text-accent rounded-lg">Resolve</button>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {tab === "disagreements" && (
        <div className="space-y-3 animate-in">
          {disagreements.length === 0 ? <p className="text-sm text-muted">No unresolved disagreements.</p> : (
            disagreements.map((d: any) => (
              <div key={d.id || d.notification_id} className="bg-card border border-border rounded-xl p-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-mono text-muted">{d.id || d.notification_id}</span>
                  <span className="px-2 py-0.5 rounded text-xs font-mono bg-orange-500/10 text-orange-500">Unresolved</span>
                </div>
                <p className="text-sm mb-2">{d.message || d.description}</p>
                <div className="flex gap-2">
                  <input value={resInput[d.id || d.notification_id] || ""} onChange={(e) => setResInput(r => ({...r, [d.id || d.notification_id]: e.target.value}))}
                    placeholder="Resolution note" className="flex-1 bg-surface border border-border rounded-lg px-3 py-1.5 text-xs" />
                  <button type="button" onClick={() => resolveDisagreement(d.id || d.notification_id)}
                    className="px-3 py-1.5 bg-accent/10 text-accent rounded-lg text-xs font-medium">Resolve</button>
                </div>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}
