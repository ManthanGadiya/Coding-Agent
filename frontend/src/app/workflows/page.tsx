"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { ListSkeleton, CardSkeleton } from "@/components/ui";

const CATEGORIES = ["sdlc", "feature", "bug_fix", "refactor", "release", "task_pipeline"];
const COMPLEXITIES = ["simple", "moderate", "complex", "critical"];

export default function WorkflowsPage() {
  const [ui, setUi] = useState<{tab: "blueprint" | "list" | "executor"; cat: string; complexity: string; blueprint: any; workflows: any[]}>({tab: "blueprint", cat: "feature", complexity: "moderate", blueprint: null, workflows: []});
  const [classify, setClassify] = useState<{input: {scope: string; risk: string; deps: number; arch: boolean; sec: boolean; research: boolean}; result: any}>({input: {scope: "medium", risk: "medium", deps: 0, arch: false, sec: false, research: false}, result: null});
  const [execInstances, setExecInstances] = useState<any[]>([]);
  const [selectedInst, setSelectedInst] = useState<any>(null);
  const [categories, setCategories] = useState<string[]>([]);
  const [createWf, setCreateWf] = useState<{show: boolean; name: string; wfType: string; description: string}>({show: false, name: "", wfType: "feature", description: ""});
  const [qualityGate, setQualityGate] = useState<{checks: string[]; input: string; result: any}>({checks: [], input: "", result: null});
  const [selectedWf, setSelectedWf] = useState<any>(null);
  const [loaded, setLoaded] = useState({workflows: false, exec: false, categories: false});

  useEffect(() => { api.workflows.list().then((d) => setUi(p => ({...p, workflows: d}))).catch(() => {}).finally(() => setLoaded(l => ({...l, workflows: true}))); }, []);
  useEffect(() => { api.executor.instances().then((d) => setExecInstances(d.instances)).catch(() => {}).finally(() => setLoaded(l => ({...l, exec: true}))); }, []);
  useEffect(() => { api.workflows.categories().then((d) => setCategories(d.categories)).catch(() => {}).finally(() => setLoaded(l => ({...l, categories: true}))); }, []);

  function refreshExec() { api.executor.instances().then((d) => setExecInstances(d.instances)).catch(() => {}); }
  function loadExecDetail(id: string) { api.executor.get(id).then(setSelectedInst).catch(() => {}); }
  function execAction(id: string, action: "pause" | "resume" | "cancel") { api.executor[action](id).then(() => { refreshExec(); if (selectedInst?.instance_id === id) loadExecDetail(id); }).catch(() => {}); }

  async function loadBlueprint() {
    const bp = await api.workflows.blueprint({ category: ui.cat, complexity: ui.complexity });
    setUi(p => ({...p, blueprint: bp}));
  }

  async function runClassify() {
    const r = await api.workflows.classify({ scope: classify.input.scope, risk: classify.input.risk, dependencies: classify.input.deps, architecture_impact: classify.input.arch, security_impact: classify.input.sec, research_needed: classify.input.research });
    setClassify(p => ({...p, result: r}));
  }

  async function doCreate() {
    if (!createWf.name.trim()) return;
    await api.workflows.create({ name: createWf.name.trim(), workflow_type: createWf.wfType, description: createWf.description.trim() });
    setCreateWf({ show: false, name: "", wfType: "feature", description: "" });
    api.workflows.list().then((d) => setUi(p => ({...p, workflows: d}))).catch(() => {});
  }

  function addGateCheck() {
    if (!qualityGate.input.trim()) return;
    setQualityGate(g => ({...g, checks: [...g.checks, g.input.trim()], input: ""}));
  }

  async function runQualityGate() {
    const r = await api.workflows.qualityGate(qualityGate.checks.map(c => ({check: c}))).catch(() => null);
    setQualityGate(g => ({...g, result: r}));
  }

  function loadWfDetail(id: string) {
    api.workflows.get(id).then(d => { setSelectedWf(d); setUi(p => ({...p, tab: "list"})); }).catch(() => {});
  }

  async function wfAction(id: string, action: "execute" | "pause" | "resume") {
    await api.workflows[action](id).catch(() => {});
    api.workflows.list().then((d) => setUi(p => ({...p, workflows: d}))).catch(() => {});
    if (selectedWf?.id === id) api.workflows.get(id).then(setSelectedWf).catch(() => {});
  }

  return (
    <div className="space-y-8">
      <div className="animate-in">
        <h1 className="text-2xl font-bold tracking-tight">Workflows</h1>
        <p className="text-muted text-sm mt-1">Blueprint builder, workflow management & execution</p>
      </div>

      <div className="flex gap-2 border-b border-border pb-2 animate-in">
        <button type="button" onClick={() => setUi(p => ({...p, tab: "blueprint"}))}
          className={`px-4 py-2 rounded-lg text-sm font-medium ${ui.tab === "blueprint" ? "bg-accent/10 text-accent" : "text-muted"}`}>Blueprint</button>
        <button type="button" onClick={() => setUi(p => ({...p, tab: "list"}))}
          className={`px-4 py-2 rounded-lg text-sm font-medium ${ui.tab === "list" ? "bg-accent/10 text-accent" : "text-muted"}`}>Workflows ({ui.workflows.length})</button>
        <button type="button" onClick={() => setUi(p => ({...p, tab: "executor"}))}
          className={`px-4 py-2 rounded-lg text-sm font-medium ${ui.tab === "executor" ? "bg-accent/10 text-accent" : "text-muted"}`}>Executor ({execInstances.length})</button>
      </div>

      {ui.tab === "blueprint" && (
        <div className="space-y-4 animate-in">
          <div className="bg-card border border-border rounded-xl p-5 space-y-4">
            <div className="flex gap-3">
              <select value={ui.cat} onChange={(e) => setUi(p => ({...p, cat: e.target.value}))} className="bg-surface border border-border rounded-lg px-3 py-2 text-sm">
                {CATEGORIES.map((c) => <option key={c} value={c}>{c.replace("_", " ")}</option>)}
              </select>
              <select value={ui.complexity} onChange={(e) => setUi(p => ({...p, complexity: e.target.value}))} className="bg-surface border border-border rounded-lg px-3 py-2 text-sm">
                {COMPLEXITIES.map((c) => <option key={c} value={c}>{c}</option>)}
              </select>
              <button type="button" onClick={loadBlueprint} className="px-5 py-2 bg-accent text-black rounded-lg text-sm font-medium">Generate</button>
            </div>
            {categories.length > 0 && (
              <div className="flex gap-1 flex-wrap">
                <span className="text-[10px] text-muted">Categories:</span>
                {categories.map((c) => <span key={c} className="text-[10px] bg-surface rounded px-1.5 py-0.5 font-mono text-muted">{c}</span>)}
              </div>
            )}
          </div>
          {ui.blueprint && (
            <div className="bg-card border border-border rounded-xl p-5">
              <div className="flex items-center gap-3 mb-4">
                <span className="text-sm font-semibold">{ui.blueprint.category}</span>
                <span className="px-2 py-0.5 rounded text-xs font-mono bg-surface">{ui.blueprint.complexity}</span>
                {ui.blueprint.requires_approval && <span className="px-2 py-0.5 rounded text-xs font-mono bg-orange-500/10 text-orange-500">requires approval</span>}
              </div>
              <div className="relative">{ui.blueprint.steps?.map((s: any, i: number) => (
                <div key={s.name} className="flex gap-4 pb-4 relative">
                  {i < ui.blueprint.steps.length - 1 && <div className="absolute left-[11px] top-6 bottom-0 w-px bg-border" />}
                  <div className="w-6 h-6 rounded-full bg-accent/20 flex items-center justify-center shrink-0 mt-0.5"><div className="w-2 h-2 rounded-full bg-accent" /></div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-medium">{s.name}</span>
                      <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-surface text-muted">{s.agent}</span>
                    </div>
                    <p className="text-xs text-muted mt-0.5">{s.description}</p>
                  </div>
                </div>
              ))}</div>
              {ui.blueprint.quality_gates?.length > 0 && (
                <div className="mt-4 pt-4 border-t border-border">
                  <div className="text-xs text-muted mb-2">Quality gates</div>
                  <div className="flex flex-wrap gap-2">{ui.blueprint.quality_gates.map((g: string) => (
                    <span key={g} className="px-2 py-1 bg-surface rounded text-xs text-muted">{g}</span>
                  ))}</div>
                </div>
              )}
            </div>
          )}
          <div className="bg-card border border-border rounded-xl p-5">
            <h2 className="text-sm font-semibold mb-3">Task Classifier</h2>
            <div className="grid grid-cols-2 gap-3 mb-3">
              <select value={classify.input.scope} onChange={(e) => setClassify(p => ({...p, input: {...p.input, scope: e.target.value}}))} className="bg-surface border border-border rounded-lg px-3 py-2 text-sm">
                <option value="small">Scope: Small</option><option value="medium">Scope: Medium</option><option value="large">Scope: Large</option>
              </select>
              <select value={classify.input.risk} onChange={(e) => setClassify(p => ({...p, input: {...p.input, risk: e.target.value}}))} className="bg-surface border border-border rounded-lg px-3 py-2 text-sm">
                <option value="low">Risk: Low</option><option value="medium">Risk: Medium</option><option value="high">Risk: High</option>
              </select>
            </div>
            <div className="flex flex-wrap gap-3 mb-3">
              <label className="flex items-center gap-2 text-sm"><input type="checkbox" checked={classify.input.arch} onChange={(e) => setClassify(p => ({...p, input: {...p.input, arch: e.target.checked}}))} className="rounded" />Architecture</label>
              <label className="flex items-center gap-2 text-sm"><input type="checkbox" checked={classify.input.sec} onChange={(e) => setClassify(p => ({...p, input: {...p.input, sec: e.target.checked}}))} className="rounded" />Security</label>
              <label className="flex items-center gap-2 text-sm"><input type="checkbox" checked={classify.input.research} onChange={(e) => setClassify(p => ({...p, input: {...p.input, research: e.target.checked}}))} className="rounded" />Research</label>
            </div>
            <div className="flex gap-2">
              <input type="number" value={classify.input.deps} onChange={(e) => setClassify(p => ({...p, input: {...p.input, deps: +e.target.value}}))} placeholder="Dependencies" aria-label="Dependencies" className="w-32 bg-surface border border-border rounded-lg px-3 py-2 text-sm" />
              <button type="button" onClick={runClassify} className="px-4 py-2 bg-accent text-black rounded-lg text-sm font-medium">Classify</button>
            </div>
            {classify.result && <div className="mt-3 text-sm">Complexity: <span className="font-mono font-bold text-accent">{classify.result.complexity}</span></div>}
          </div>

          <div className="bg-card border border-border rounded-xl p-5">
            <h2 className="text-sm font-semibold mb-3">Quality Gate</h2>
            <div className="flex gap-2 mb-3">
              <input aria-label="Quality gate check description" value={qualityGate.input} onChange={(e) => setQualityGate(g => ({...g, input: e.target.value}))}
                placeholder="Check description" className="flex-1 bg-surface border border-border rounded-lg px-3 py-2 text-sm"
                onKeyDown={(e) => e.key === "Enter" && addGateCheck()} />
              <button type="button" onClick={addGateCheck} className="px-3 py-2 bg-surface border border-border rounded-lg text-sm">Add</button>
            </div>
            {qualityGate.checks.length > 0 && (
              <div className="space-y-1 mb-3">{qualityGate.checks.map((c, i) => (
                <div key={c ?? i} className="flex items-center gap-2 text-xs font-mono bg-surface rounded-lg px-3 py-1.5">
                  <span className="text-accent">{i + 1}.</span>
                  <span className="flex-1">{c}</span>
                  <button type="button" onClick={() => setQualityGate(g => ({...g, checks: g.checks.filter((_, j) => j !== i)}))} className="text-red-500">✕</button>
                </div>
              ))}</div>
            )}
            <div className="flex gap-2">
              <button type="button" onClick={runQualityGate} disabled={qualityGate.checks.length === 0}
                className="px-4 py-2 bg-accent text-black rounded-lg text-sm font-medium disabled:opacity-40">Evaluate</button>
              <button type="button" onClick={() => { api.workflows.recommend().then((r) => setQualityGate(g => ({...g, result: r}))).catch(() => {}); }}
                className="px-4 py-2 bg-surface border border-border rounded-lg text-sm">Recommend</button>
            </div>
            {qualityGate.result && <pre className="mt-3 text-xs font-mono bg-surface rounded-lg p-3 text-muted max-h-40 overflow-auto">{JSON.stringify(qualityGate.result, null, 2)}</pre>}
          </div>
        </div>
      )}

      {ui.tab === "executor" && (
        <div className="space-y-4 animate-in">
          <div className="flex gap-2 items-center">
            <input id="execName" aria-label="Workflow name to execute" placeholder="workflow name" className="bg-surface border border-border rounded-lg px-3 py-2 text-sm flex-1"
              onKeyDown={(e) => { if (e.key === "Enter") { const inp = document.getElementById("execName") as HTMLInputElement; api.executor.run(inp.value).then(() => { inp.value = ""; refreshExec(); }); }}} />
            <button type="button" onClick={refreshExec} className="px-3 py-2 bg-surface border border-border rounded-lg text-sm">Refresh</button>
          </div>
          {selectedInst && (
            <div className="bg-card border border-border rounded-xl p-5">
              <div className="flex items-center justify-between mb-3">
                <h2 className="text-sm font-semibold">{selectedInst.instance_id}</h2>
                <button type="button" onClick={() => setSelectedInst(null)} className="text-xs text-muted hover:text-foreground">Close</button>
              </div>
              <div className="grid grid-cols-3 gap-3 mb-3">
                <div className="bg-surface rounded-lg p-3">
                  <div className="text-[10px] text-muted">Status</div>
                  <div className={`text-sm font-mono mt-1 ${selectedInst.status === "completed" ? "text-success" : selectedInst.status === "running" ? "text-accent" : selectedInst.status === "failed" ? "text-red-500" : "text-yellow-500"}`}>{selectedInst.status}</div>
                </div>
                <div className="bg-surface rounded-lg p-3">
                  <div className="text-[10px] text-muted">Current Step</div>
                  <div className="text-sm font-mono mt-1">{selectedInst.current_step ?? "-"}/{selectedInst.steps?.length ?? "-"}</div>
                </div>
                <div className="bg-surface rounded-lg p-3">
                  <div className="text-[10px] text-muted">Workflow</div>
                  <div className="text-sm font-mono mt-1 truncate">{selectedInst.workflow_name ?? "-"}</div>
                </div>
              </div>
              {selectedInst.steps && (
                <div className="space-y-2 mb-3">
                  <div className="text-xs text-muted">Steps</div>
                  {selectedInst.steps.map((s: any, i: number) => (
                    <div key={s.name ?? s.step_name ?? i} className="flex items-center gap-3 bg-surface rounded-lg px-3 py-2">
                      <div className={`w-2 h-2 rounded-full ${s.status === "completed" ? "bg-success" : s.status === "failed" ? "bg-red-500" : s.status === "running" ? "bg-accent animate-pulse" : "bg-yellow-500"}`} />
                      <span className="text-xs font-mono flex-1">{s.name ?? s.step_name ?? `step-${i}`}</span>
                {s.attempts > 1 && <span className="text-[10px] text-muted">retry {s.attempts}</span>}
                {s.error && <span className="text-[10px] text-red-400 truncate max-w-[200px]" title={s.error}>{s.error}</span>}
              </div>
            ))}
          </div>
        )}
        <div className="flex gap-2">
          {selectedInst.status === "running" && <button type="button" onClick={() => execAction(selectedInst.instance_id, "pause")} className="px-3 py-1.5 bg-yellow-500/10 text-yellow-500 rounded-lg text-xs font-medium">Pause</button>}
          {selectedInst.status === "paused" && <button type="button" onClick={() => execAction(selectedInst.instance_id, "resume")} className="px-3 py-1.5 bg-accent/10 text-accent rounded-lg text-xs font-medium">Resume</button>}
          {(selectedInst.status === "running" || selectedInst.status === "paused") && <button type="button" onClick={() => execAction(selectedInst.instance_id, "cancel")} className="px-3 py-1.5 bg-red-500/10 text-red-500 rounded-lg text-xs font-medium">Cancel</button>}
        </div>
            </div>
          )}
          {execInstances.length === 0 && !selectedInst && (
            loaded.exec ? <p className="text-sm text-muted py-8 text-center">No executor instances. Run a workflow to see instances here.</p> : <ListSkeleton rows={2} />
          )}
          {execInstances.map((inst: any) => (
            <button type="button" className="w-full text-left bg-card border border-border rounded-xl p-4 hover:border-accent/30 transition-colors" onClick={() => loadExecDetail(inst.instance_id)}>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-mono truncate flex-1">{inst.instance_id}</span>
                <span className={`px-2 py-0.5 rounded-full text-xs font-mono ${inst.status === "completed" ? "bg-success/10 text-success" : inst.status === "running" ? "bg-accent/10 text-accent" : inst.status === "failed" ? "bg-red-500/10 text-red-500" : inst.status === "cancelled" ? "bg-muted/10 text-muted" : "bg-yellow-500/10 text-yellow-500"}`}>{inst.status}</span>
              </div>
              <div className="flex gap-3 text-[10px] text-muted font-mono">
                <span>Workflow: {inst.workflow_name}</span>
                <span>Step: {inst.current_step}/{inst.steps_completed ?? "?"}</span>
              </div>
            </button>
          ))}
        </div>
      )}

      {ui.tab === "list" && (
        <div className="space-y-4 animate-in">
          <button type="button" onClick={() => setCreateWf(c => ({...c, show: !c.show}))}
            className="px-4 py-2 bg-accent text-black rounded-lg text-sm font-medium">{createWf.show ? "Cancel" : "+ Create Workflow"}</button>
          {createWf.show && (
            <div className="bg-card border border-border rounded-xl p-5 space-y-3">
              <input aria-label="New workflow name" value={createWf.name} onChange={(e) => setCreateWf(c => ({...c, name: e.target.value}))}
                placeholder="Workflow name" className="w-full bg-surface border border-border rounded-lg px-3 py-2 text-sm" />
              <select aria-label="Workflow category" value={createWf.wfType} onChange={(e) => setCreateWf(c => ({...c, wfType: e.target.value}))}
                className="bg-surface border border-border rounded-lg px-3 py-2 text-sm">
                {CATEGORIES.map((c) => <option key={c} value={c}>{c.replace("_", " ")}</option>)}
              </select>
              <textarea aria-label="Workflow description" value={createWf.description} onChange={(e) => setCreateWf(c => ({...c, description: e.target.value}))}
                placeholder="Description" className="w-full bg-surface border border-border rounded-lg px-3 py-2 text-sm min-h-[60px]" />
              <button type="button" onClick={doCreate} disabled={!createWf.name.trim()}
                className="px-4 py-2 bg-accent text-black rounded-lg text-sm font-medium disabled:opacity-40">Create</button>
            </div>
          )}
          {selectedWf && (
            <div className="bg-card border border-border rounded-xl p-5">
              <div className="flex items-center justify-between mb-3">
                <h2 className="text-sm font-semibold">{selectedWf.name}</h2>
                <button type="button" onClick={() => setSelectedWf(null)} className="text-xs text-muted hover:text-foreground">Close</button>
              </div>
              <div className="grid grid-cols-3 gap-3 mb-3">
                <div className="bg-surface rounded-lg p-3">
                  <div className="text-[10px] text-muted">Status</div>
                  <div className={`text-sm font-mono mt-1 capitalize ${selectedWf.status === "completed" ? "text-success" : selectedWf.status === "running" ? "text-accent" : selectedWf.status === "failed" ? "text-red-500" : "text-yellow-500"}`}>{selectedWf.status}</div>
                </div>
                <div className="bg-surface rounded-lg p-3">
                  <div className="text-[10px] text-muted">Type</div>
                  <div className="text-sm font-mono mt-1">{selectedWf.workflow_type}</div>
                </div>
                <div className="bg-surface rounded-lg p-3">
                  <div className="text-[10px] text-muted">Steps</div>
                  <div className="text-sm font-mono mt-1">{selectedWf.current_step}/{selectedWf.total_steps}</div>
                </div>
              </div>
              {selectedWf.description && <p className="text-sm text-muted mb-3">{selectedWf.description}</p>}
              <div className="flex gap-2">
                {selectedWf.status !== "running" && selectedWf.status !== "completed" && (
                  <button type="button" onClick={() => wfAction(selectedWf.id, "execute")} className="px-3 py-1.5 bg-accent/10 text-accent rounded-lg text-xs font-medium">Execute</button>
                )}
                {selectedWf.status === "running" && <button type="button" onClick={() => wfAction(selectedWf.id, "pause")} className="px-3 py-1.5 bg-yellow-500/10 text-yellow-500 rounded-lg text-xs font-medium">Pause</button>}
                {selectedWf.status === "paused" && <button type="button" onClick={() => wfAction(selectedWf.id, "resume")} className="px-3 py-1.5 bg-accent/10 text-accent rounded-lg text-xs font-medium">Resume</button>}
              </div>
            </div>
          )}
          {ui.workflows.length === 0 && !selectedWf && (
            loaded.workflows ? <p className="text-sm text-muted py-8 text-center">No workflows yet. Create one above or generate a blueprint.</p> : <ListSkeleton rows={3} />
          )}
          {ui.workflows.map((wf: any) => (
            <button type="button" className="w-full text-left bg-card border border-border rounded-xl p-4 hover:border-accent/30 transition-colors" onClick={() => loadWfDetail(wf.id)}>
              <div className="flex items-center justify-between mb-2">
                <div>
                  <span className="text-sm font-medium">{wf.name}</span>
                  <span className="ml-2 text-[10px] font-mono text-muted">{wf.workflow_type}</span>
                </div>
                <span className={`px-2 py-0.5 rounded-full text-xs font-mono ${wf.status === "completed" ? "bg-success/10 text-success" : wf.status === "running" ? "bg-accent/10 text-accent" : wf.status === "failed" ? "bg-red-500/10 text-red-500" : "bg-yellow-500/10 text-yellow-500"}`}>{wf.status}</span>
              </div>
              <p className="text-xs text-muted">{wf.description}</p>
              <div className="flex gap-2 mt-2 text-[10px] text-muted font-mono">
                <span>Steps: {wf.current_step}/{wf.total_steps}</span>
                <span>Agents: {(wf.assigned_agents || []).join(", ")}</span>
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
