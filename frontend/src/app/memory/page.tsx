"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { api } from "@/lib/api";

const categoryColor: Record<string, string> = {
  architecture: "text-purple-400",
  decision: "text-blue-400",
  lesson: "text-green-400",
  bug: "text-error",
  preference: "text-accent",
  pattern: "text-cyan-400",
  insight: "text-pink-400",
  general: "text-muted",
};

export default function Memory() {
  const [data, setData] = useState({ entries: [] as any[], loading: true, filter: "", searchQ: "" });
  const [create, setCreate] = useState({ show: false, title: "", content: "", category: "general" });

  const loadEntries = useCallback(async (filterValue?: string) => {
    setData(d => ({...d, loading: true}));
    try {
      const f = filterValue ?? data.filter;
      const params = f ? `category=${f}` : "";
      const d: any = await api.memory.entries(params);
      setData(x => ({...x, entries: Array.isArray(d) ? d : d.entries ?? []}));
    } catch { setData(d => ({...d, entries: []})); }
    finally { setData(d => ({...d, loading: false})); }
  }, [data.filter]);

  const loadRef = useRef(loadEntries);
  loadRef.current = loadEntries;
  useEffect(() => { loadRef.current(); }, []);

  async function search() {
    if (!data.searchQ.trim()) { loadEntries(); return; }
    setData(d => ({...d, loading: true}));
    try {
      const d: any = await api.memory.search(data.searchQ.trim());
      setData(x => ({...x, entries: Array.isArray(d) ? d : d.entries ?? d}));
    } catch { setData(d => ({...d, entries: []})); }
    finally { setData(d => ({...d, loading: false})); }
  }

  async function createEntry() {
    if (!create.title.trim() || !create.content.trim()) return;
    await fetch("/api/v1/memory/entries", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ scope: "global", category: create.category, title: create.title.trim(), content: create.content.trim() }),
    });
    setCreate(c => ({...c, title: "", content: "", show: false}));
    loadEntries();
  }

  return (
    <div className="space-y-6 animate-in">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold tracking-tight">Memory</h1>
        <button type="button" onClick={() => setCreate(c => ({...c, show: !c.show}))}
          className="px-4 py-2 bg-accent text-black font-medium rounded-lg text-sm hover:brightness-110 transition-all">
          {create.show ? "Cancel" : "+ New Entry"}
        </button>
      </div>

      {create.show && (
        <div className="bg-card border border-border rounded-xl p-5 space-y-3">
          <input aria-label="Entry title" className="w-full bg-surface border border-border rounded-lg px-4 py-2.5 text-sm outline-none focus:border-accent"
            placeholder="Title" value={create.title} onChange={(e) => setCreate(c => ({...c, title: e.target.value}))} />
          <textarea aria-label="Entry content" className="w-full bg-surface border border-border rounded-lg px-4 py-2.5 text-sm outline-none focus:border-accent min-h-[80px] resize-y"
            placeholder="Content" value={create.content} onChange={(e) => setCreate(c => ({...c, content: e.target.value}))} />
          <div className="flex gap-2 items-center">
            <select aria-label="Category" className="bg-surface border border-border rounded-lg px-3 py-2 text-sm outline-none"
              value={create.category} onChange={(e) => setCreate(c => ({...c, category: e.target.value}))}>
              {["general", "architecture", "decision", "lesson", "bug", "preference", "pattern", "insight"].map(c =>
                <option key={c} value={c}>{c}</option>
              )}
            </select>
            <button type="button" onClick={createEntry} disabled={!create.title.trim() || !create.content.trim()}
              className="px-4 py-2 bg-accent text-black font-medium rounded-lg text-sm disabled:opacity-40">
              Create
            </button>
          </div>
        </div>
      )}

      <div className="flex gap-3">
        <div className="flex gap-2 flex-wrap flex-1">
          {["", "general", "architecture", "decision", "lesson", "bug", "preference"].map((c) => (
            <button key={c} type="button" onClick={() => { setData(d => ({...d, filter: c, searchQ: ""})); loadEntries(c); }}
              className={`px-3 py-1.5 rounded-lg text-xs font-mono transition-colors ${
                data.filter === c ? "bg-accent text-black" : "bg-card border border-border text-muted hover:text-foreground"
              }`}>{c || "all"}</button>
          ))}
        </div>
        <div className="flex gap-2">
          <input aria-label="Search memory" className="bg-surface border border-border rounded-lg px-3 py-1.5 text-xs outline-none focus:border-accent w-48"
            placeholder="Search..." value={data.searchQ} onChange={(e) => setData(d => ({...d, searchQ: e.target.value}))}
            onKeyDown={(e) => e.key === "Enter" && search()} />
          <button type="button" onClick={search}
            className="px-3 py-1.5 bg-card border border-border rounded-lg text-xs font-mono hover:text-foreground transition-colors">
            Search
          </button>
        </div>
      </div>

      {data.loading ? (
        <div className="text-center text-muted text-sm py-12">Loading...</div>
      ) : data.entries.length === 0 ? (
        <div className="text-center text-muted text-sm py-12">No memory entries found</div>
      ) : (
        <div className="bg-card border border-border rounded-xl divide-y divide-border">
          {data.entries.map((e: any) => (
            <div key={e.id} className="px-5 py-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <code className="text-sm font-mono text-accent">{e.title || e.key}</code>
                  <span className={`text-[10px] font-mono ${categoryColor[e.category] || "text-muted"}`}>
                    {e.category}
                  </span>
                </div>
                <div className="flex items-center gap-3 text-[10px] text-muted font-mono">
                  {e.confidence && <span>confidence: {typeof e.confidence === "string" ? e.confidence : e.confidence.toFixed(2)}</span>}
                  {e.created_at && <span>{new Date(e.created_at).toLocaleDateString()}</span>}
                </div>
              </div>
              <div className="text-sm text-muted mt-1 line-clamp-2">{e.content || e.value}</div>
              {e.tags && e.tags.length > 0 && (
                <div className="flex gap-1.5 mt-2 flex-wrap">
                  {(Array.isArray(e.tags) ? e.tags : []).slice(0, 5).map((tag: string) => (
                    <span key={tag} className="text-[10px] bg-surface border border-border rounded px-1.5 py-0.5 font-mono text-muted">
                      {tag}
                    </span>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
