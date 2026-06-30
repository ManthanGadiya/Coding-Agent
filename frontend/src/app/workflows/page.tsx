"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";

const CATEGORIES = ["sdlc", "feature", "bug_fix", "refactor", "release", "task_pipeline"];
const COMPLEXITIES = ["simple", "moderate", "complex", "critical"];

export default function WorkflowsPage() {
  const [ui, setUi] = useState<{tab: "blueprint" | "list"; cat: string; complexity: string; blueprint: any; workflows: any[]}>({tab: "blueprint" as "blueprint" | "list", cat: "feature", complexity: "moderate", blueprint: null, workflows: []});
  const [classify, setClassify] = useState<{input: {scope: string; risk: string; deps: number; arch: boolean; sec: boolean; research: boolean}; result: any}>({input: {scope: "medium", risk: "medium", deps: 0, arch: false, sec: false, research: false}, result: null});

  useEffect(() => { api.workflows.list().then((d) => setUi((prev) => ({...prev, workflows: d}))).catch(() => {}); }, []);

  async function loadBlueprint() {
    const bp = await api.workflows.blueprint({ category: ui.cat, complexity: ui.complexity });
    setUi((prev) => ({...prev, blueprint: bp}));
  }

  async function runClassify() {
    const r = await api.workflows.classify({
      scope: classify.input.scope, risk: classify.input.risk,
      dependencies: classify.input.deps, architecture_impact: classify.input.arch,
      security_impact: classify.input.sec, research_needed: classify.input.research,
    });
    setClassify((prev) => ({...prev, result: r}));
  }

  return (
    <div className="space-y-8">
      <div className="animate-in">
        <h1 className="text-2xl font-bold tracking-tight">Workflows</h1>
        <p className="text-muted text-sm mt-1">Blueprint builder & workflow management</p>
      </div>

      <div className="flex gap-2 border-b border-border pb-2 animate-in">
        <button type="button" onClick={() => setUi((prev) => ({...prev, tab: "blueprint"}))}
          className={`px-4 py-2 rounded-lg text-sm font-medium ${ui.tab === "blueprint" ? "bg-accent/10 text-accent" : "text-muted"}`}>Blueprint</button>
        <button type="button" onClick={() => setUi((prev) => ({...prev, tab: "list"}))}
          className={`px-4 py-2 rounded-lg text-sm font-medium ${ui.tab === "list" ? "bg-accent/10 text-accent" : "text-muted"}`}>Workflows ({ui.workflows.length})</button>
      </div>

      {ui.tab === "blueprint" && (
        <div className="space-y-4 animate-in">
          <div className="bg-card border border-border rounded-xl p-5 space-y-4">
            <div className="flex gap-3">
              <select value={ui.cat} onChange={(e) => setUi((prev) => ({...prev, cat: e.target.value}))} className="bg-surface border border-border rounded-lg px-3 py-2 text-sm">
                {CATEGORIES.map((c) => <option key={c} value={c}>{c.replace("_", " ")}</option>)}
              </select>
              <select value={ui.complexity} onChange={(e) => setUi((prev) => ({...prev, complexity: e.target.value}))} className="bg-surface border border-border rounded-lg px-3 py-2 text-sm">
                {COMPLEXITIES.map((c) => <option key={c} value={c}>{c}</option>)}
              </select>
              <button type="button" onClick={loadBlueprint} className="px-5 py-2 bg-accent text-black rounded-lg text-sm font-medium">Generate</button>
            </div>

            {["bug_fix", "refactor", "release"].includes(ui.cat) && (
              <div className="text-xs text-muted">
                {ui.cat === "bug_fix" && "Tip: use severity=critical|high|medium|low via API for tailored bug fix workflows"}
                {ui.cat === "refactor" && "Tip: use impact=high|moderate|low via API for tailored refactor workflows"}
                {ui.cat === "release" && "Tip: use release_type=major|minor|patch via API for tailored release workflows"}
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

              <div className="relative">
                {ui.blueprint.steps.map((s: any, i: number) => (
                  <div key={s.name} className="flex gap-4 pb-4 relative">
                    {i < ui.blueprint.steps.length - 1 && <div className="absolute left-[11px] top-6 bottom-0 w-px bg-border" />}
                    <div className="w-6 h-6 rounded-full bg-accent/20 flex items-center justify-center shrink-0 mt-0.5">
                      <div className="w-2 h-2 rounded-full bg-accent" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-medium">{s.name}</span>
                        <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-surface text-muted">{s.agent}</span>
                      </div>
                      <p className="text-xs text-muted mt-0.5">{s.description}</p>
                    </div>
                  </div>
                ))}
              </div>

              {ui.blueprint.quality_gates?.length > 0 && (
                <div className="mt-4 pt-4 border-t border-border">
                  <div className="text-xs text-muted mb-2">Quality gates</div>
                  <div className="flex flex-wrap gap-2">
                    {ui.blueprint.quality_gates.map((g: string) => (
                      <span key={g} className="px-2 py-1 bg-surface rounded text-xs text-muted">{g}</span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          <div className="bg-card border border-border rounded-xl p-5">
            <h2 className="text-sm font-semibold mb-3">Task Classifier</h2>
            <div className="grid grid-cols-2 gap-3 mb-3">
              <select value={classify.input.scope} onChange={(e) => setClassify((prev) => ({...prev, input: {...prev.input, scope: e.target.value}}))}
                className="bg-surface border border-border rounded-lg px-3 py-2 text-sm">
                <option value="small">Scope: Small</option>
                <option value="medium">Scope: Medium</option>
                <option value="large">Scope: Large</option>
              </select>
              <select value={classify.input.risk} onChange={(e) => setClassify((prev) => ({...prev, input: {...prev.input, risk: e.target.value}}))}
                className="bg-surface border border-border rounded-lg px-3 py-2 text-sm">
                <option value="low">Risk: Low</option>
                <option value="medium">Risk: Medium</option>
                <option value="high">Risk: High</option>
              </select>
            </div>
            <div className="flex flex-wrap gap-3 mb-3">
              <label className="flex items-center gap-2 text-sm"><input type="checkbox" checked={classify.input.arch}
                onChange={(e) => setClassify((prev) => ({...prev, input: {...prev.input, arch: e.target.checked}}))} className="rounded" />Architecture impact</label>
              <label className="flex items-center gap-2 text-sm"><input type="checkbox" checked={classify.input.sec}
                onChange={(e) => setClassify((prev) => ({...prev, input: {...prev.input, sec: e.target.checked}}))} className="rounded" />Security impact</label>
              <label className="flex items-center gap-2 text-sm"><input type="checkbox" checked={classify.input.research}
                onChange={(e) => setClassify((prev) => ({...prev, input: {...prev.input, research: e.target.checked}}))} className="rounded" />Research needed</label>
            </div>
            <div className="flex gap-2">
              <input type="number" value={classify.input.deps} onChange={(e) => setClassify((prev) => ({...prev, input: {...prev.input, deps: +e.target.value}}))}
                placeholder="Dependencies" aria-label="Number of dependencies"
                className="w-32 bg-surface border border-border rounded-lg px-3 py-2 text-sm" />
              <button type="button" onClick={runClassify} className="px-4 py-2 bg-accent text-black rounded-lg text-sm font-medium">Classify</button>
            </div>
            {classify.result && (
              <div className="mt-3 text-sm">
                Complexity: <span className="font-mono font-bold text-accent">{classify.result.complexity}</span>
              </div>
            )}
          </div>
        </div>
      )}

      {ui.tab === "list" && (
        <div className="space-y-3 animate-in">
          {ui.workflows.length === 0 && <p className="text-sm text-muted">No workflows created yet.</p>}
          {ui.workflows.map((wf: any) => (
            <div key={wf.id} className="bg-card border border-border rounded-xl p-4">
              <div className="flex items-center justify-between mb-2">
                <div>
                  <span className="text-sm font-medium">{wf.name}</span>
                  <span className="ml-2 text-[10px] font-mono text-muted">{wf.workflow_type}</span>
                </div>
                <span className={`px-2 py-0.5 rounded-full text-xs font-mono ${
                  wf.status === "completed" ? "bg-success/10 text-success" :
                  wf.status === "running" ? "bg-accent/10 text-accent" :
                  wf.status === "failed" ? "bg-red-500/10 text-red-500" : "bg-yellow-500/10 text-yellow-500"
                }`}>{wf.status}</span>
              </div>
              <p className="text-xs text-muted">{wf.description}</p>
              <div className="flex gap-2 mt-2 text-[10px] text-muted font-mono">
                <span>Steps: {wf.current_step}/{wf.total_steps}</span>
                <span>Agents: {(wf.assigned_agents || []).join(", ")}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
