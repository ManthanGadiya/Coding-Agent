"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { AgentProfile, RetrievalResult } from "@/lib/api";

const AGENTS = ["manager", "architect", "planner", "coder", "tester", "debugger", "reviewer", "memory"];
const MODES = ["planning", "architecture", "implementation", "testing", "debugging", "review", "learning", "research", "optimization"];

type MemoryHit = RetrievalResult & { tags?: string[]; factors?: Record<string, number> };

type RetrieveResponse = {
  memories: MemoryHit[];
  confidence: number;
  contradictions?: unknown[];
  summary?: string;
};

export default function MemoryRetrievalPage() {
  const [params, setParams] = useState({ query: "", agent: "", mode: "", complexity: "moderate" });
  const [result, setResult] = useState<RetrieveResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [profiles, setProfiles] = useState<Record<string, AgentProfile>>({});

  useEffect(() => { api.memoryRetrieval.profiles().then(setProfiles).catch(() => {}); }, []);

  async function search() {
    setLoading(true);
    try {
      const r = await api.memoryRetrieval.retrieve({ query: params.query, agent: params.agent, mode: params.mode, task_complexity: params.complexity });
      setResult({ memories: (r.memories ?? []) as MemoryHit[], confidence: r.confidence ?? 0, contradictions: r.contradictions, summary: r.summary });
    } catch { setResult(null); }
    setLoading(false);
  }

  return (
    <div className="space-y-8">
      <div className="animate-in">
        <h1 className="text-2xl font-bold tracking-tight">Memory Retrieval</h1>
        <p className="text-muted text-sm mt-1">Weighted 7-factor memory search with agent-aware profiles</p>
      </div>

      <div className="bg-card border border-border rounded-xl p-5 space-y-4 animate-in">
        <div className="flex gap-3">
          <input value={params.query} onChange={(e) => setParams(p => ({...p, query: e.target.value}))} onKeyDown={(e) => e.key === "Enter" && search()}
            placeholder="Search memories..."
            aria-label="Search query"
            className="flex-1 bg-surface border border-border rounded-lg px-4 py-2.5 text-sm" />
          <button type="button" onClick={search} disabled={loading || !params.query}
            className="px-5 py-2.5 bg-accent text-black rounded-lg text-sm font-medium disabled:opacity-50">
            {loading ? "Searching..." : "Retrieve"}
          </button>
        </div>

        <div className="flex gap-3 flex-wrap">
          <select aria-label="Agent filter" value={params.agent} onChange={(e) => setParams(p => ({...p, agent: e.target.value}))} className="bg-surface border border-border rounded-lg px-3 py-2 text-sm">
            <option value="">Any agent</option>
            {AGENTS.map((a) => <option key={a} value={a}>{a}</option>)}
          </select>
          <select aria-label="Mode filter" value={params.mode} onChange={(e) => setParams(p => ({...p, mode: e.target.value}))} className="bg-surface border border-border rounded-lg px-3 py-2 text-sm">
            <option value="">Any mode</option>
            {MODES.map((m) => <option key={m} value={m}>{m}</option>)}
          </select>
          <select aria-label="Complexity filter" value={params.complexity} onChange={(e) => setParams(p => ({...p, complexity: e.target.value}))} className="bg-surface border border-border rounded-lg px-3 py-2 text-sm">
            <option value="simple">Simple</option>
            <option value="moderate">Moderate</option>
            <option value="complex">Complex</option>
            <option value="large">Large</option>
          </select>
        </div>
      </div>

      {result && (
        <div className="space-y-4 animate-in">
          <div className="flex gap-3 flex-wrap">
            <div className="bg-card border border-border rounded-xl px-4 py-3">
              <div className="text-xs text-muted">Memories</div>
              <div className="text-lg font-mono font-bold text-accent">{result.memories.length}</div>
            </div>
            <div className="bg-card border border-border rounded-xl px-4 py-3">
              <div className="text-xs text-muted">Confidence</div>
              <div className="text-lg font-mono font-bold">{result.confidence}</div>
            </div>
            <div className="bg-card border border-border rounded-xl px-4 py-3">
              <div className="text-xs text-muted">Contradictions</div>
              <div className="text-lg font-mono font-bold">{result.contradictions?.length || 0}</div>
            </div>
          </div>

          {result.summary && (
            <div className="bg-card border border-border rounded-xl p-4">
              <div className="text-xs text-muted mb-1">Summary</div>
              <p className="text-sm">{result.summary}</p>
            </div>
          )}

          {result.memories.map((m) => (
            <div key={m.id} className="bg-card border border-border rounded-xl p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-mono text-muted">{m.id}</span>
                <span className="text-xs font-mono text-accent">score: {m.score}</span>
              </div>
              <p className="text-sm">{m.content}</p>
              {m.tags && m.tags.length > 0 && (
                <div className="flex flex-wrap gap-1 mt-2">
                  {m.tags.map((t) => <span key={t} className="px-2 py-0.5 bg-surface rounded text-xs text-muted">{t}</span>)}
                </div>
              )}
              {m.factors && (
                <div className="flex flex-wrap gap-2 mt-2 text-[10px] font-mono text-muted">
                  {Object.entries(m.factors).map(([k, v]) => (
                    <span key={k}>{k}: {v}</span>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {Object.keys(profiles).length > 0 && (
        <div className="bg-card border border-border rounded-xl p-5 animate-in">
          <h2 className="text-sm font-semibold mb-3">Agent Profiles</h2>
          <div className="grid grid-cols-2 gap-2 text-xs">
            {Object.entries(profiles).map(([agent, prefs]) => (
              <div key={agent} className="bg-surface rounded-lg p-3">
                <div className="font-medium mb-1 text-accent">{agent}</div>
                {Object.entries(prefs).map(([k, v]) => (
                  <div key={k} className="flex justify-between"><span className="text-muted">{k}</span><span className="font-mono">{String(v ?? "")}</span></div>
                ))}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
