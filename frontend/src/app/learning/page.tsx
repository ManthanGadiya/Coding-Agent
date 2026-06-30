"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";

export default function LearningPage() {
  const [data, setData] = useState<{tab: "failures" | "lessons" | "metrics" | "proposals"; failures: any[]; lessons: any[]; metrics: any[]; proposals: any[]}>({tab: "failures", failures: [], lessons: [], metrics: [], proposals: []});
  const [why, setWhy] = useState<{whys: any[] | null; input: string}>({whys: null, input: ""});

  useEffect(() => {
    api.learning.failures().then((d) => setData((prev) => ({...prev, failures: d}))).catch(() => {});
    api.learning.lessons("status=active").then((d) => setData((prev) => ({...prev, lessons: d}))).catch(() => {});
    api.learning.metrics().then((d) => setData((prev) => ({...prev, metrics: d}))).catch(() => {});
    api.learning.proposals().then((d) => setData((prev) => ({...prev, proposals: d}))).catch(() => {});
  }, []);

  const tabs = [
    { key: "failures" as const, label: "Failures", count: data.failures.length },
    { key: "lessons" as const, label: "Lessons", count: data.lessons.length },
    { key: "metrics" as const, label: "Metrics", count: data.metrics.length },
    { key: "proposals" as const, label: "Proposals", count: data.proposals.length },
  ];

  return (
    <div className="space-y-8">
      <div className="animate-in">
        <h1 className="text-2xl font-bold tracking-tight">Learning System</h1>
        <p className="text-muted text-sm mt-1">Failure analysis, lessons, metrics & improvements</p>
      </div>

      <div className="flex gap-2 border-b border-border pb-2 animate-in">
        {tabs.map((t) => (
          <button key={t.key} type="button" onClick={() => setData((prev) => ({...prev, tab: t.key}))}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
              data.tab === t.key ? "bg-accent/10 text-accent" : "text-muted hover:text-foreground"
            }`}
          >
            {t.label} <span className="text-xs font-mono ml-1 opacity-60">{t.count}</span>
          </button>
        ))}
      </div>

      {data.tab === "failures" && (
        <div className="space-y-3 animate-in">
          <div className="bg-card border border-border rounded-xl p-5">
            <h2 className="text-sm font-semibold mb-3">5 Whys Analysis</h2>
            <div className="flex gap-2">
              <input value={why.input} onChange={(e) => setWhy((prev) => ({...prev, input: e.target.value}))}
                placeholder="Paste problem description (one line per why)..."
                aria-label="Problem description for 5 Whys analysis"
                className="flex-1 bg-surface border border-border rounded-lg px-3 py-2 text-sm" />
              <button type="button" onClick={async () => { const r: any = await api.learning.fiveWhys(why.input); setWhy((prev) => ({...prev, whys: r})); }}
                className="px-4 py-2 bg-accent text-black rounded-lg text-sm font-medium">Analyze</button>
            </div>
            {why.whys && (
              <div className="mt-3 space-y-1">
                {why.whys.map((w: any, i: number) => (
                  <div key={w.question} className="flex gap-2 text-sm"><span className="text-accent font-mono shrink-0">{w.question}:</span><span>{w.answer}</span></div>
                ))}
              </div>
            )}
          </div>
          {data.failures.length === 0 && <p className="text-sm text-muted">No failures recorded.</p>}
          {data.failures.map((f: any) => (
            <div key={f.failure_id} className="bg-card border border-border rounded-xl p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-mono text-muted">{f.failure_id}</span>
                <span className={`px-2 py-0.5 rounded-full text-xs font-mono ${
                  f.severity === "critical" ? "bg-red-500/10 text-red-500" :
                  f.severity === "high" ? "bg-orange-500/10 text-orange-500" : "bg-yellow-500/10 text-yellow-500"
                }`}>{f.severity}</span>
              </div>
              <p className="text-sm font-medium">{f.description}</p>
              <p className="text-xs text-muted mt-1">Root cause: {f.root_cause}</p>
              {f.preventive_actions?.length > 0 && (
                <div className="mt-2 flex flex-wrap gap-1">
                  {f.preventive_actions.map((a: string) => (
                    <span key={a} className="px-2 py-0.5 bg-surface rounded text-xs text-muted">{a}</span>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {data.tab === "lessons" && (
        <div className="space-y-3 animate-in">
          {data.lessons.length === 0 && <p className="text-sm text-muted">No active lessons.</p>}
          {data.lessons.map((l: any) => (
            <div key={l.lesson_id} className="bg-card border border-border rounded-xl p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-mono text-muted">{l.lesson_id}</span>
                <div className="flex gap-2">
                  <span className="px-2 py-0.5 rounded text-xs font-mono bg-surface">{l.scope}</span>
                  <span className={`px-2 py-0.5 rounded text-xs font-mono ${
                    l.confidence === "high" ? "bg-success/10 text-success" : "bg-yellow-500/10 text-yellow-500"
                  }`}>{l.confidence}</span>
                </div>
              </div>
              <p className="text-sm font-medium">{l.topic}</p>
              <p className="text-xs text-muted mt-1">{l.description.slice(0, 200)}</p>
            </div>
          ))}
        </div>
      )}

      {data.tab === "metrics" && (
        <div className="animate-in">
          {data.metrics.length === 0 ? <p className="text-sm text-muted">No metrics recorded.</p> : (
            <div className="space-y-3">
              {data.metrics.slice().reverse().map((m: any) => (
                <div key={m.timestamp ?? m.id} className="bg-card border border-border rounded-xl p-4">
                  <div className="text-xs font-mono text-muted mb-2">{m.timestamp}</div>
                  <div className="text-2xl font-mono font-bold text-accent">{m.overall}</div>
                  <div className="mt-2 flex flex-wrap gap-2">
                    {Object.entries(m.categories).map(([k, v]: [string, any]) => (
                      <div key={k} className="text-xs"><span className="text-muted">{k}:</span> <span className="font-mono">{v}</span></div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {data.tab === "proposals" && (
        <div className="space-y-3 animate-in">
          {data.proposals.length === 0 && <p className="text-sm text-muted">No improvement proposals.</p>}
          {data.proposals.map((p: any) => (
            <div key={p.proposal_id} className="bg-card border border-border rounded-xl p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-mono text-muted">{p.proposal_id}</span>
                <span className={`px-2 py-0.5 rounded-full text-xs font-mono ${
                  p.status === "approved" ? "bg-success/10 text-success" :
                  p.status === "rejected" ? "bg-red-500/10 text-red-500" : "bg-yellow-500/10 text-yellow-500"
                }`}>{p.status}</span>
              </div>
              <p className="text-sm font-medium">{p.observation}</p>
              <p className="text-xs text-muted mt-1">{p.expected_benefit}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
