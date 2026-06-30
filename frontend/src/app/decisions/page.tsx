"use client";
import { useCallback, useEffect, useState } from "react";
import { api } from "@/lib/api";
import { ListSkeleton, CardSkeleton } from "@/components/ui";

export default function DecisionsPage() {
  const [tab, setTab] = useState<"history" | "decide" | "risk">("history");
  const [history, setHistory] = useState<any[]>([]);
  const [loaded, setLoaded] = useState(false);

  // Decide form
  const [decision, setDecision] = useState<{objective: string; options: {label: string; desc: string; risk: string}[]; optLabel: string; optDesc: string; optRisk: string; result: any}>({
    objective: "", options: [], optLabel: "", optDesc: "", optRisk: "medium", result: null,
  });

  // Risk form
  const [risk, setRisk] = useState<{action: string; result: any}>({action: "", result: null});

  useEffect(() => {
    api.decisions.history().then((d) => setHistory(Array.isArray(d) ? d : [])).catch(() => {}).finally(() => setLoaded(true));
  }, []);

  function addOption() {
    if (!decision.optLabel.trim()) return;
    setDecision(d => ({
      ...d,
      options: [...d.options, {label: d.optLabel.trim(), desc: d.optDesc.trim(), risk: d.optRisk}],
      optLabel: "", optDesc: "", optRisk: "medium",
    }));
  }

  const makeDecision = useCallback(async () => {
    if (!decision.objective.trim() || decision.options.length < 1) return;
    const r = await api.decisions.decide(decision.objective.trim(), decision.options).catch((e) => ({error: e.message}));
    setDecision(d => ({...d, result: r}));
    api.decisions.history().then((d) => setHistory(Array.isArray(d) ? d : [])).catch(() => {});
  }, [decision.objective, decision.options]);

  const assessRisk = useCallback(async () => {
    if (!risk.action.trim()) return;
    const r = await api.decisions.assessRisk(risk.action.trim()).catch((e) => ({error: e.message}));
    setRisk(p => ({...p, result: r}));
  }, [risk.action]);

  return (
    <div className="space-y-8">
      <div className="animate-in">
        <h1 className="text-2xl font-bold tracking-tight">Decisions</h1>
        <p className="text-muted text-sm mt-1">Decision history, risk assessment & decision engine</p>
      </div>

      <div className="flex gap-2 border-b border-border pb-2 animate-in">
        {([{key: "history", label: "History"}, {key: "decide", label: "Decide"}, {key: "risk", label: "Risk"}]).map(t => (
          <button key={t.key} type="button" onClick={() => setTab(t.key as typeof tab)}
            className={`px-4 py-2 rounded-lg text-sm font-medium capitalize ${tab === t.key ? "bg-accent/10 text-accent" : "text-muted hover:text-foreground"}`}>
            {t.label}
          </button>
        ))}
      </div>

      {tab === "history" && (
        <div className="space-y-3 animate-in">
          {!loaded ? <ListSkeleton rows={4} /> : history.length === 0 ? (
            <p className="text-sm text-muted py-8 text-center">No decisions recorded yet. Use the Decide tab to make your first decision.</p>
          ) : history.map((h: any, i: number) => (
            <div key={h.id || i} className="bg-card border border-border rounded-xl p-5">
              <div className="flex items-center justify-between mb-3">
                <h3 className="font-semibold text-sm">{h.objective || h.context || "Decision"}</h3>
                <span className="text-[10px] font-mono text-muted">{h.timestamp ? new Date(h.timestamp).toLocaleString() : ""}</span>
              </div>
              {h.options && (
                <div className="space-y-1 mb-3">{h.options.map((o: any, j: number) => (
                  <div key={j} className="flex items-center gap-2 text-xs bg-surface rounded-lg px-3 py-2">
                    <span className="text-accent font-mono">{j + 1}.</span>
                    <span className="flex-1">{o.label || o.name}</span>
                    {o.risk && <span className={`px-1.5 py-0.5 rounded text-[10px] font-mono ${o.risk === "low" ? "bg-success/10 text-success" : o.risk === "high" ? "bg-red-500/10 text-red-500" : "bg-yellow-500/10 text-yellow-500"}`}>{o.risk}</span>}
                  </div>
                ))}</div>
              )}
              {h.selected && <div className="text-xs font-mono text-accent">Selected: {h.selected}</div>}
              {h.decision && <div className="text-xs font-mono text-accent">Decision: {h.decision}</div>}
              {h.risk_score != null && <div className="text-xs font-mono mt-2">Risk: <span className={`font-bold ${h.risk_score > 0.6 ? "text-red-500" : h.risk_score > 0.3 ? "text-yellow-500" : "text-success"}`}>{(h.risk_score * 100).toFixed(0)}%</span></div>}
            </div>
          ))}
        </div>
      )}

      {tab === "decide" && (
        <div className="space-y-4 animate-in">
          <div className="bg-card border border-border rounded-xl p-5 space-y-4">
            <h2 className="text-sm font-semibold">Make a Decision</h2>
            <input value={decision.objective} onChange={(e) => setDecision(d => ({...d, objective: e.target.value}))}
              placeholder="What decision needs to be made?" className="w-full bg-surface border border-border rounded-lg px-3 py-2 text-sm" />

            <div className="space-y-2">
              <div className="text-xs text-muted">Options ({decision.options.length})</div>
              {decision.options.length > 0 && (
                <div className="space-y-1 mb-2">{decision.options.map((o, i) => (
                  <div key={i} className="flex items-center gap-2 text-xs bg-surface rounded-lg px-3 py-2">
                    <span className="text-accent font-mono">{i + 1}.</span>
                    <span className="flex-1">{o.label}{o.desc ? ` — ${o.desc}` : ""}</span>
                    <span className={`px-1.5 py-0.5 rounded text-[10px] font-mono ${o.risk === "low" ? "bg-success/10 text-success" : o.risk === "high" ? "bg-red-500/10 text-red-500" : "bg-yellow-500/10 text-yellow-500"}`}>{o.risk}</span>
                    <button type="button" onClick={() => setDecision(d => ({...d, options: d.options.filter((_, j) => j !== i)}))} className="text-red-500">✕</button>
                  </div>
                ))}</div>
              )}
              <div className="flex gap-2">
                <input value={decision.optLabel} onChange={(e) => setDecision(d => ({...d, optLabel: e.target.value}))}
                  placeholder="Option label" className="flex-1 bg-surface border border-border rounded-lg px-3 py-2 text-sm"
                  onKeyDown={(e) => e.key === "Enter" && addOption()} />
                <input value={decision.optDesc} onChange={(e) => setDecision(d => ({...d, optDesc: e.target.value}))}
                  placeholder="Description (optional)" className="flex-1 bg-surface border border-border rounded-lg px-3 py-2 text-sm" />
                <select value={decision.optRisk} onChange={(e) => setDecision(d => ({...d, optRisk: e.target.value}))}
                  className="bg-surface border border-border rounded-lg px-3 py-2 text-sm">
                  <option value="low">Low Risk</option><option value="medium">Medium Risk</option><option value="high">High Risk</option>
                </select>
                <button type="button" onClick={addOption} className="px-3 py-2 bg-surface border border-border rounded-lg text-sm">Add</button>
              </div>
            </div>

            <button type="button" onClick={makeDecision} disabled={!decision.objective.trim() || decision.options.length < 1}
              className="px-5 py-2 bg-accent text-black rounded-lg text-sm font-medium disabled:opacity-40">Decide</button>

            {decision.result && (
              <div className="bg-surface rounded-lg p-4 space-y-2">
                <div className="text-xs font-semibold text-accent">Decision Result</div>
                <pre className="text-xs font-mono text-muted max-h-60 overflow-auto">{JSON.stringify(decision.result, null, 2)}</pre>
              </div>
            )}
          </div>
        </div>
      )}

      {tab === "risk" && (
        <div className="space-y-4 animate-in">
          <div className="bg-card border border-border rounded-xl p-5 space-y-4">
            <h2 className="text-sm font-semibold">Risk Assessment</h2>
            <p className="text-xs text-muted">Assess the risk of an action or decision before committing to it.</p>
            <div className="flex gap-2">
              <input value={risk.action} onChange={(e) => setRisk(p => ({...p, action: e.target.value}))}
                placeholder="Describe the action to assess..." className="flex-1 bg-surface border border-border rounded-lg px-3 py-2 text-sm"
                onKeyDown={(e) => e.key === "Enter" && assessRisk()} />
              <button type="button" onClick={assessRisk} disabled={!risk.action.trim()}
                className="px-4 py-2 bg-accent text-black rounded-lg text-sm font-medium disabled:opacity-40">Assess</button>
            </div>
            {risk.result && (
              <div className="bg-surface rounded-lg p-4 space-y-2">
                <div className="text-xs font-semibold">Assessment</div>
                <pre className="text-xs font-mono text-muted max-h-60 overflow-auto">{JSON.stringify(risk.result, null, 2)}</pre>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
