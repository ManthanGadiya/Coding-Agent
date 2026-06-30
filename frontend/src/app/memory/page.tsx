"use client";
import { useCallback, useEffect, useRef, useState } from "react";
import { api } from "@/lib/api";
import { ListSkeleton, Skeleton } from "@/components/ui";

const categoryColor: Record<string, string> = {
  architecture: "text-purple-400", decision: "text-blue-400", lesson: "text-green-400",
  bug: "text-error", preference: "text-accent", pattern: "text-cyan-400", insight: "text-pink-400", general: "text-muted",
};

export default function MemoryPage() {
  const [data, setData] = useState({ entries: [] as any[], loading: true, filter: "", searchQ: "" });
  const [create, setCreate] = useState({ show: false, title: "", content: "", category: "general" });
  const [tab, setTab] = useState<"entries" | "retention" | "compress">("entries");
  const [retention, setRetention] = useState<any>(null);
  const [stale, setStale] = useState<any[]>([]);
  const [archival, setArchival] = useState<any[]>([]);
  const [compressResult, setCompressResult] = useState<any>(null);
  const [selected, setSelected] = useState<any>(null);
  const [versions, setVersions] = useState<any[]>([]);

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

  useEffect(() => {
    if (tab === "retention") {
      api.memory.retentionHealth().then(setRetention).catch(() => {});
      api.memory.stale().then((d: any) => setStale(Array.isArray(d) ? d : [])).catch(() => {});
      api.memory.archivalCandidates().then((d: any) => setArchival(Array.isArray(d) ? d : [])).catch(() => {});
    }
  }, [tab]);

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
    await api.memory.createEntry({ scope: "global", category: create.category, title: create.title.trim(), content: create.content.trim() });
    setCreate(c => ({...c, title: "", content: "", show: false}));
    loadEntries();
  }

  async function deleteEntry(id: string) {
    await api.memory.deleteEntry(id).catch(() => {});
    setSelected(null);
    loadEntries();
  }

  async function loadVersions(id: string) {
    api.memory.versions(id).then(setVersions).catch(() => {});
  }

  return (
    <div className="space-y-8">
      <div className="animate-in">
        <h1 className="text-2xl font-bold tracking-tight">Memory</h1>
        <p className="text-muted text-sm mt-1">Knowledge store, retention & compression</p>
      </div>

      <div className="flex gap-2 border-b border-border pb-2 animate-in">
        {(["entries", "retention", "compress"] as const).map(t => (
          <button key={t} type="button" onClick={() => setTab(t)}
            className={`px-4 py-2 rounded-lg text-sm font-medium capitalize ${tab === t ? "bg-accent/10 text-accent" : "text-muted hover:text-foreground"}`}>{t}</button>
        ))}
      </div>

      {tab === "entries" && (
        <div className="space-y-6 animate-in">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-semibold">Entries</h2>
            <button type="button" onClick={() => setCreate(c => ({...c, show: !c.show}))}
              className="px-4 py-2 bg-accent text-black font-medium rounded-lg text-sm hover:brightness-110 transition-all">
              {create.show ? "Cancel" : "+ New Entry"}
            </button>
          </div>

          {create.show && (
            <div className="bg-card border border-border rounded-xl p-5 space-y-3">
              <input aria-label="Title" className="w-full bg-surface border border-border rounded-lg px-4 py-2.5 text-sm outline-none focus:border-accent"
                placeholder="Title" value={create.title} onChange={(e) => setCreate(c => ({...c, title: e.target.value}))} />
              <textarea aria-label="Content" className="w-full bg-surface border border-border rounded-lg px-4 py-2.5 text-sm outline-none focus:border-accent min-h-[80px] resize-y"
                placeholder="Content" value={create.content} onChange={(e) => setCreate(c => ({...c, content: e.target.value}))} />
              <div className="flex gap-2 items-center">
                <select aria-label="Category" className="bg-surface border border-border rounded-lg px-3 py-2 text-sm outline-none"
                  value={create.category} onChange={(e) => setCreate(c => ({...c, category: e.target.value}))}>
                  {["general", "architecture", "decision", "lesson", "bug", "preference", "pattern", "insight"].map(c =>
                    <option key={c} value={c}>{c}</option>)}
                </select>
                <button type="button" onClick={createEntry} disabled={!create.title.trim() || !create.content.trim()}
                  className="px-4 py-2 bg-accent text-black font-medium rounded-lg text-sm disabled:opacity-40">Create</button>
              </div>
            </div>
          )}

          <div className="flex gap-3">
            <div className="flex gap-2 flex-wrap flex-1">
              {["", "general", "architecture", "decision", "lesson", "bug", "preference"].map((c) => (
                <button key={c} type="button" onClick={() => { setData(d => ({...d, filter: c, searchQ: ""})); loadEntries(c); }}
                  className={`px-3 py-1.5 rounded-lg text-xs font-mono transition-colors ${data.filter === c ? "bg-accent text-black" : "bg-card border border-border text-muted hover:text-foreground"}`}>{c || "all"}</button>
              ))}
            </div>
            <div className="flex gap-2">
              <input aria-label="Search" className="bg-surface border border-border rounded-lg px-3 py-1.5 text-xs outline-none focus:border-accent w-48"
                placeholder="Search..." value={data.searchQ} onChange={(e) => setData(d => ({...d, searchQ: e.target.value}))}
                onKeyDown={(e) => e.key === "Enter" && search()} />
              <button type="button" onClick={search} className="px-3 py-1.5 bg-card border border-border rounded-lg text-xs font-mono">Search</button>
            </div>
          </div>

          {selected ? (
            <div className="bg-card border border-border rounded-xl p-5 space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <code className="text-sm font-mono text-accent">{selected.title || selected.key}</code>
                  <span className={`text-[10px] font-mono ${categoryColor[selected.category] || "text-muted"}`}>{selected.category}</span>
                </div>
                <button type="button" onClick={() => { setSelected(null); setVersions([]); }} className="text-xs text-muted hover:text-foreground">Close</button>
              </div>
              <p className="text-sm text-muted whitespace-pre-wrap">{selected.content || selected.value}</p>
              <div className="flex gap-3 text-[10px] text-muted font-mono">
                <span>ID: {selected.id}</span>
                {selected.confidence && <span>Confidence: {typeof selected.confidence === "string" ? selected.confidence : selected.confidence.toFixed(2)}</span>}
                {selected.created_at && <span>{new Date(selected.created_at).toLocaleString()}</span>}
              </div>
              <div className="flex gap-2">
                <button type="button" onClick={() => loadVersions(selected.id)}
                  className="px-3 py-1.5 bg-accent/10 text-accent rounded-lg text-xs font-medium">Versions</button>
                <button type="button" onClick={() => deleteEntry(selected.id)}
                  className="px-3 py-1.5 bg-red-500/10 text-red-500 rounded-lg text-xs font-medium">Delete</button>
              </div>
              {versions.length > 0 && (
                <div className="space-y-1 border-t border-border pt-3">
                  <div className="text-xs text-muted mb-1">Version History ({versions.length})</div>
                  {versions.map((v: any, i: number) => (
                    <div key={v.version_id || i} className="text-xs font-mono text-muted bg-surface rounded-lg px-3 py-2">
                      v{i + 1} — {new Date(v.created_at || v.timestamp).toLocaleString()}
                    </div>
                  ))}
                </div>
              )}
            </div>
          ) : data.loading ? (
            <ListSkeleton rows={4} />
          ) : data.entries.length === 0 ? (
            <div className="text-center text-muted text-sm py-12">No memory entries yet. Create your first entry above.</div>
          ) : (
            <div className="bg-card border border-border rounded-xl divide-y divide-border">
              {data.entries.map((e: any) => (
                <div key={e.id} className="px-5 py-4 cursor-pointer hover:bg-card-hover transition-colors" onClick={() => { setSelected(e); setVersions([]); }}>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <code className="text-sm font-mono text-accent">{e.title || e.key}</code>
                      <span className={`text-[10px] font-mono ${categoryColor[e.category] || "text-muted"}`}>{e.category}</span>
                    </div>
                    <div className="flex items-center gap-3 text-[10px] text-muted font-mono">
                      {e.confidence && <span>confidence: {typeof e.confidence === "string" ? e.confidence : e.confidence.toFixed(2)}</span>}
                      {e.created_at && <span>{new Date(e.created_at).toLocaleDateString()}</span>}
                    </div>
                  </div>
                  <div className="text-sm text-muted mt-1 line-clamp-2">{e.content || e.value}</div>
                  {e.tags?.length > 0 && (
                    <div className="flex gap-1.5 mt-2 flex-wrap">
                      {(Array.isArray(e.tags) ? e.tags : []).slice(0, 5).map((tag: string) => (
                        <span key={tag} className="text-[10px] bg-surface border border-border rounded px-1.5 py-0.5 font-mono text-muted">{tag}</span>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {tab === "retention" && (
        <div className="space-y-4 animate-in">
          {retention && (
            <div className="bg-card border border-border rounded-xl p-5">
              <h2 className="text-sm font-semibold mb-3">Retention Health</h2>
              <div className="grid grid-cols-3 gap-3">
                {Object.entries(retention).filter(([k]) => typeof retention[k] === "number").map(([k, v]) => (
                  <div key={k} className="bg-surface rounded-lg p-3">
                    <div className="text-[10px] text-muted capitalize">{k.replace(/_/g, " ")}</div>
                    <div className="text-lg font-mono font-bold text-accent mt-1">{v as number}</div>
                  </div>
                ))}
              </div>
            </div>
          )}
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-card border border-border rounded-xl p-5">
              <h2 className="text-sm font-semibold mb-3">Stale Entries ({stale.length})</h2>
              {stale.length === 0 ? <p className="text-xs text-muted">No stale entries.</p> : (
                <div className="space-y-2">
                  {stale.slice(0, 10).map((s: any) => (
                    <div key={s.id} className="text-xs font-mono bg-surface rounded-lg px-3 py-2 text-muted">{s.title || s.id}</div>
                  ))}
                </div>
              )}
            </div>
            <div className="bg-card border border-border rounded-xl p-5">
              <h2 className="text-sm font-semibold mb-3">Archival Candidates ({archival.length})</h2>
              {archival.length === 0 ? <p className="text-xs text-muted">No archival candidates.</p> : (
                <div className="space-y-2">
                  {archival.slice(0, 10).map((a: any) => (
                    <div key={a.id} className="text-xs font-mono bg-surface rounded-lg px-3 py-2 text-muted">{a.title || a.id}</div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {tab === "compress" && (
        <div className="space-y-4 animate-in">
          <div className="bg-card border border-border rounded-xl p-5 space-y-4">
            <h2 className="text-sm font-semibold">Compression</h2>
            <div className="flex gap-2">
              <button type="button" onClick={() => api.memory.compress().then(setCompressResult).catch(() => {})}
                className="px-4 py-2 bg-accent text-black rounded-lg text-sm font-medium">Run Compression</button>
              <button type="button" onClick={() => api.memory.suggestCompress().then(setCompressResult).catch(() => {})}
                className="px-4 py-2 bg-surface border border-border rounded-lg text-sm">Suggest</button>
            </div>
            {compressResult && (
              <pre className="text-xs font-mono bg-surface rounded-lg p-3 text-muted max-h-60 overflow-auto">{JSON.stringify(compressResult, null, 2)}</pre>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
