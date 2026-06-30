"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";

export default function ReleasesPage() {
  const [tab, setTab] = useState<"pipeline" | "release">("pipeline");
  const [pipelines, setPipelines] = useState<any[]>([]);
  const [selectedPipe, setSelectedPipe] = useState<any>(null);
  const [pipeCategory, setPipeCategory] = useState("feature");
  const [pipeComplexity, setPipeComplexity] = useState("moderate");
  const [candidates, setCandidates] = useState<any[]>([]);
  const [version, setVersion] = useState("");
  const [relType, setRelType] = useState("patch");
  const [selectedCandidate, setSelectedCandidate] = useState<any>(null);
  const [checkName, setCheckName] = useState("");

  useEffect(() => { api.pipelines.listActive().then((d) => setPipelines(d.pipelines)).catch(() => {}); }, []);

  function createPipeline() {
    api.pipelines.create(pipeCategory, pipeComplexity).then(() =>
      api.pipelines.listActive().then((d) => setPipelines(d.pipelines))
    ).catch(() => {});
  }
  function loadPipe(id: string) { api.pipelines.get(id).then(setSelectedPipe).catch(() => {}); }
  function transitionPipe(id: string, status: string) {
    api.pipelines.transition(id, status).then(() => loadPipe(id)).catch(() => {});
  }
  function unblockPipe(id: string) { api.pipelines.unblock(id).then(() => loadPipe(id)).catch(() => {}); }
  function rollbackPipe(id: string) { api.pipelines.rollback(id).then(() => loadPipe(id)).catch(() => {}); }

  function createCandidate() {
    api.releases.candidate(version, relType).then((rc: any) => {
      setCandidates((prev) => [...prev, rc]); setSelectedCandidate(rc); setVersion("");
    }).catch(() => {});
  }
  function loadCandidate(id: string) { api.releases.getCandidate(id).then(setSelectedCandidate).catch(() => {}); }
  function setCheck() {
    if (!selectedCandidate || !checkName) return;
    api.releases.setCheck(selectedCandidate.id, checkName, true).then(() => loadCandidate(selectedCandidate.id)).catch(() => {});
    setCheckName("");
  }
  function approveCandidate() { api.releases.approve(selectedCandidate.id, "manager").then(() => loadCandidate(selectedCandidate.id)).catch(() => {}); }
  function deployCandidate() { api.releases.deploy(selectedCandidate.id).then(() => loadCandidate(selectedCandidate.id)).catch(() => {}); }
  function rollbackCandidate() { api.releases.rollback(selectedCandidate.id, "manual").then(() => loadCandidate(selectedCandidate.id)).catch(() => {}); }

  return (
    <div className="space-y-8">
      <div className="animate-in">
        <h1 className="text-2xl font-bold tracking-tight">Releases</h1>
        <p className="text-muted text-sm mt-1">Pipeline lifecycle & release candidate management</p>
      </div>

      <div className="flex gap-2 border-b border-border pb-2 animate-in">
        <button type="button" onClick={() => setTab("pipeline")}
          className={`px-4 py-2 rounded-lg text-sm font-medium ${tab === "pipeline" ? "bg-accent/10 text-accent" : "text-muted"}`}>Pipelines ({pipelines.length})</button>
        <button type="button" onClick={() => setTab("release")}
          className={`px-4 py-2 rounded-lg text-sm font-medium ${tab === "release" ? "bg-accent/10 text-accent" : "text-muted"}`}>Release Candidates ({candidates.length})</button>
      </div>

      {tab === "pipeline" && (
        <div className="space-y-4 animate-in">
          <div className="bg-card border border-border rounded-xl p-5">
            <h2 className="text-sm font-semibold mb-3">Create Pipeline</h2>
            <div className="flex gap-2">
              <select value={pipeCategory} onChange={(e) => setPipeCategory(e.target.value)}
                className="bg-surface border border-border rounded-lg px-3 py-2 text-sm">
                {["feature", "bug_fix", "refactor", "release", "sdlc"].map((c) => <option key={c} value={c}>{c}</option>)}
              </select>
              <select value={pipeComplexity} onChange={(e) => setPipeComplexity(e.target.value)}
                className="bg-surface border border-border rounded-lg px-3 py-2 text-sm">
                {["simple", "moderate", "complex"].map((c) => <option key={c} value={c}>{c}</option>)}
              </select>
              <button type="button" onClick={createPipeline}
                className="px-4 py-2 bg-accent text-black rounded-lg text-sm font-medium">Create</button>
            </div>
          </div>

          {selectedPipe && (
            <div className="bg-card border border-border rounded-xl p-5">
              <div className="flex items-center justify-between mb-3">
                <h2 className="text-sm font-semibold">{selectedPipe.id}</h2>
                <div className="flex gap-2">
                  <button type="button" onClick={() => setSelectedPipe(null)} className="text-xs text-muted">Close</button>
                </div>
              </div>
              <div className="grid grid-cols-4 gap-2 mb-3">
                <div className="bg-surface rounded-lg p-3">
                  <div className="text-[10px] text-muted">Category</div>
                  <div className="text-sm font-mono">{selectedPipe.category}</div>
                </div>
                <div className="bg-surface rounded-lg p-3">
                  <div className="text-[10px] text-muted">Complexity</div>
                  <div className="text-sm font-mono">{selectedPipe.complexity}</div>
                </div>
                <div className="bg-surface rounded-lg p-3">
                  <div className="text-[10px] text-muted">State</div>
                  <div className={`text-sm font-mono ${selectedPipe.state === "completed" ? "text-success" : selectedPipe.state === "blocked" ? "text-red-500" : "text-accent"}`}>{selectedPipe.state}</div>
                </div>
                <div className="bg-surface rounded-lg p-3">
                  <div className="text-[10px] text-muted">Step</div>
                  <div className="text-sm font-mono">{selectedPipe.current_step}/{selectedPipe.total_steps}</div>
                </div>
              </div>

              {selectedPipe.steps && (
                <div className="space-y-1 mb-3">
                  {selectedPipe.steps.map((s: any, i: number) => (
                    <div key={i} className="text-xs font-mono bg-surface rounded px-3 py-1.5">{s}</div>
                  ))}
                </div>
              )}

              <div className="flex gap-2">
                {selectedPipe.state === "running" && (
                  <button type="button" onClick={() => transitionPipe(selectedPipe.id, "completed")}
                    className="px-3 py-1.5 bg-success/10 text-success rounded-lg text-xs font-medium">Complete Step</button>
                )}
                {selectedPipe.state !== "blocked" && selectedPipe.state !== "completed" && (
                  <button type="button" onClick={() => unblockPipe(selectedPipe.id)}
                    className="px-3 py-1.5 bg-yellow-500/10 text-yellow-500 rounded-lg text-xs font-medium">Unblock</button>
                )}
                {selectedPipe.current_step > 0 && (
                  <button type="button" onClick={() => rollbackPipe(selectedPipe.id)}
                    className="px-3 py-1.5 bg-red-500/10 text-red-500 rounded-lg text-xs font-medium">Rollback</button>
                )}
              </div>
            </div>
          )}

          {pipelines.map((p: any) => (
            <div key={p.id} onClick={() => loadPipe(p.id)}
              className="bg-card border border-border rounded-xl p-4 cursor-pointer hover:border-accent/30">
              <div className="flex items-center justify-between">
                <span className="text-sm font-mono">{p.id}</span>
                <div className="flex gap-3 text-[10px] text-muted font-mono">
                  <span>{p.category}</span>
                  <span className={`px-2 py-0.5 rounded-full text-xs ${
                    p.state === "completed" ? "bg-success/10 text-success" :
                    p.state === "blocked" ? "bg-red-500/10 text-red-500" : "bg-accent/10 text-accent"
                  }`}>{p.state}</span>
                  <span>Step {p.current_step}/{p.total_steps}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {tab === "release" && (
        <div className="space-y-4 animate-in">
          <div className="bg-card border border-border rounded-xl p-5">
            <h2 className="text-sm font-semibold mb-3">Create Release Candidate</h2>
            <div className="flex gap-2">
              <input value={version} onChange={(e) => setVersion(e.target.value)} placeholder="e.g. 1.2.3"
                className="bg-surface border border-border rounded-lg px-3 py-2 text-sm w-32" />
              <select value={relType} onChange={(e) => setRelType(e.target.value)}
                className="bg-surface border border-border rounded-lg px-3 py-2 text-sm">
                <option value="patch">Patch</option>
                <option value="minor">Minor</option>
                <option value="major">Major</option>
              </select>
              <button type="button" onClick={createCandidate} disabled={!version}
                className="px-4 py-2 bg-accent text-black rounded-lg text-sm font-medium disabled:opacity-40">Create</button>
            </div>
          </div>

          {selectedCandidate && (
            <div className="bg-card border border-border rounded-xl p-5">
              <div className="flex items-center justify-between mb-3">
                <h2 className="text-sm font-semibold">Candidate {selectedCandidate.id}</h2>
                <button type="button" onClick={() => setSelectedCandidate(null)} className="text-xs text-muted">Close</button>
              </div>
              <div className="grid grid-cols-3 gap-2 mb-3">
                <div className="bg-surface rounded-lg p-3">
                  <div className="text-[10px] text-muted">Version</div>
                  <div className="text-sm font-mono">{selectedCandidate.version}</div>
                </div>
                <div className="bg-surface rounded-lg p-3">
                  <div className="text-[10px] text-muted">Status</div>
                  <div className="text-sm font-mono">{selectedCandidate.status}</div>
                </div>
                <div className="bg-surface rounded-lg p-3">
                  <div className="text-[10px] text-muted">Release Type</div>
                  <div className="text-sm font-mono">{selectedCandidate.release_type}</div>
                </div>
              </div>

              {selectedCandidate.checks && (
                <div className="mb-3">
                  <div className="text-xs text-muted mb-1">Checks</div>
                  <div className="flex flex-wrap gap-2">
                    {Object.entries(selectedCandidate.checks).map(([k, v]) => (
                      <span key={k} className={`px-2 py-1 rounded text-xs font-mono ${v ? "bg-success/10 text-success" : "bg-red-500/10 text-red-500"}`}>{k}: {v ? "pass" : "fail"}</span>
                    ))}
                  </div>
                </div>
              )}

              <div className="flex gap-2 mb-3">
                <input value={checkName} onChange={(e) => setCheckName(e.target.value)} placeholder="Check name"
                  className="bg-surface border border-border rounded-lg px-3 py-1.5 text-xs flex-1" />
                <button type="button" onClick={setCheck} disabled={!checkName}
                  className="px-3 py-1.5 bg-accent/10 text-accent rounded-lg text-xs font-medium disabled:opacity-40">Add Check</button>
              </div>

              <div className="flex gap-2">
                <button type="button" onClick={approveCandidate}
                  className="px-3 py-1.5 bg-success/10 text-success rounded-lg text-xs font-medium">Approve</button>
                <button type="button" onClick={deployCandidate}
                  className="px-3 py-1.5 bg-accent/10 text-accent rounded-lg text-xs font-medium">Deploy</button>
                <button type="button" onClick={rollbackCandidate}
                  className="px-3 py-1.5 bg-red-500/10 text-red-500 rounded-lg text-xs font-medium">Rollback</button>
              </div>
            </div>
          )}

          {candidates.length === 0 && <p className="text-sm text-muted">No release candidates yet.</p>}
        </div>
      )}
    </div>
  );
}
