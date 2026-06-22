"use client";

import { useEffect, useState } from "react";
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
  const [entries, setEntries] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState("");
  const [searchQ, setSearchQ] = useState("");
  const [showCreate, setShowCreate] = useState(false);
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [category, setCategory] = useState("general");

  useEffect(() => { loadEntries(); }, [filter]);

  async function loadEntries() {
    setLoading(true);
    try {
      const params = filter ? `category=${filter}` : "";
      const d: any = await api.memory.entries(params);
      setEntries(Array.isArray(d) ? d : d.entries ?? []);
    } catch { setEntries([]); }
    finally { setLoading(false); }
  }

  async function search() {
    if (!searchQ.trim()) { loadEntries(); return; }
    setLoading(true);
    try {
      const d: any = await api.memory.search(searchQ.trim());
      setEntries(Array.isArray(d) ? d : d.entries ?? d);
    } catch { setEntries([]); }
    finally { setLoading(false); }
  }

  async function createEntry() {
    if (!title.trim() || !content.trim()) return;
    await fetch("/api/v1/memory/entries", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ scope: "global", category, title: title.trim(), content: content.trim() }),
    });
    setTitle(""); setContent(""); setShowCreate(false);
    loadEntries();
  }

  return (
    <div className="space-y-6 animate-in">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold tracking-tight">Memory</h1>
        <button onClick={() => setShowCreate(!showCreate)}
          className="px-4 py-2 bg-accent text-black font-medium rounded-lg text-sm hover:brightness-110 transition-all">
          {showCreate ? "Cancel" : "+ New Entry"}
        </button>
      </div>

      {showCreate && (
        <div className="bg-card border border-border rounded-xl p-5 space-y-3">
          <input className="w-full bg-surface border border-border rounded-lg px-4 py-2.5 text-sm outline-none focus:border-accent"
            placeholder="Title" value={title} onChange={(e) => setTitle(e.target.value)} />
          <textarea className="w-full bg-surface border border-border rounded-lg px-4 py-2.5 text-sm outline-none focus:border-accent min-h-[80px] resize-y"
            placeholder="Content" value={content} onChange={(e) => setContent(e.target.value)} />
          <div className="flex gap-2 items-center">
            <select className="bg-surface border border-border rounded-lg px-3 py-2 text-sm outline-none"
              value={category} onChange={(e) => setCategory(e.target.value)}>
              {["general", "architecture", "decision", "lesson", "bug", "preference", "pattern", "insight"].map(c =>
                <option key={c} value={c}>{c}</option>
              )}
            </select>
            <button onClick={createEntry} disabled={!title.trim() || !content.trim()}
              className="px-4 py-2 bg-accent text-black font-medium rounded-lg text-sm disabled:opacity-40">
              Create
            </button>
          </div>
        </div>
      )}

      <div className="flex gap-3">
        <div className="flex gap-2 flex-wrap flex-1">
          {["", "general", "architecture", "decision", "lesson", "bug", "preference"].map((c) => (
            <button key={c} type="button" onClick={() => { setFilter(c); setSearchQ(""); }}
              className={`px-3 py-1.5 rounded-lg text-xs font-mono transition-colors ${
                filter === c ? "bg-accent text-black" : "bg-card border border-border text-muted hover:text-foreground"
              }`}>{c || "all"}</button>
          ))}
        </div>
        <div className="flex gap-2">
          <input className="bg-surface border border-border rounded-lg px-3 py-1.5 text-xs outline-none focus:border-accent w-48"
            placeholder="Search..." value={searchQ} onChange={(e) => setSearchQ(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && search()} />
          <button onClick={search}
            className="px-3 py-1.5 bg-card border border-border rounded-lg text-xs font-mono hover:text-foreground transition-colors">
            Search
          </button>
        </div>
      </div>

      {loading ? (
        <div className="text-center text-muted text-sm py-12">Loading...</div>
      ) : entries.length === 0 ? (
        <div className="text-center text-muted text-sm py-12">No memory entries found</div>
      ) : (
        <div className="bg-card border border-border rounded-xl divide-y divide-border">
          {entries.map((e: any) => (
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
