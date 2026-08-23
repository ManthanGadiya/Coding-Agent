"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { CandidateRule, ImprovementProposal, KnowledgeArtifact, LearningFailure, LearningMetric, Lesson } from "@/lib/api";
import { ListSkeleton } from "@/components/ui";

// ponytail: legacy endpoints may wrap lists in an envelope; real fix is correcting api.ts return types
function unwrapList<T>(d: unknown[] | Record<string, unknown>, key: string): T[] {
  return Array.isArray(d) ? (d as T[]) : ((d[key] as T[] | undefined) ?? []);
}

type WhyPair = { question: string; answer: string };
type FailureRow = LearningFailure & { failure_id?: string; preventive_actions?: string[] };
type LessonRow = Lesson & { lesson_id?: string; topic?: string; description?: string };
type MetricRow = LearningMetric & { timestamp?: string; overall?: number; categories?: Record<string, string | number> };
type ProposalRow = ImprovementProposal & { proposal_id?: string; observation?: string; expected_benefit?: string };
type ArtifactRow = KnowledgeArtifact & { artifact_id?: string; topic?: string };
type RuleRow = CandidateRule & { rule_id?: string };

export default function LearningPage() {
  const [data, setData] = useState<{tab: "failures" | "lessons" | "metrics" | "proposals" | "knowledge" | "rules"; failures: FailureRow[]; lessons: LessonRow[]; metrics: MetricRow[]; proposals: ProposalRow[]; artifacts: ArtifactRow[]; pendingRules: RuleRow[]; approvedRules: RuleRow[]}>({tab: "failures", failures: [], lessons: [], metrics: [], proposals: [], artifacts: [], pendingRules: [], approvedRules: []});
  const [why, setWhy] = useState<{whys: WhyPair[] | null; input: string}>({whys: null, input: ""});
  const [createLesson, setCreateLesson] = useState<{show: boolean; topic: string; description: string; scope: string}>({show: false, topic: "", description: "", scope: "project"});
  const [proposalReview, setProposalReview] = useState<Record<string, string>>({});
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    Promise.all([
      api.learning.failures().then((d) => setData(p => ({...p, failures: Array.isArray(d) ? d : []}))).catch(() => {}),
      api.learning.lessons("status=active").then((d) => setData(p => ({...p, lessons: Array.isArray(d) ? d : []}))).catch(() => {}),
      api.learning.metrics().then((d) => setData(p => ({...p, metrics: Array.isArray(d) ? d : []}))).catch(() => {}),
      api.learning.proposals().then((d) => setData(p => ({...p, proposals: Array.isArray(d) ? d : []}))).catch(() => {}),
    ]).finally(() => setLoaded(true));
  }, []);

  useEffect(() => {
    if (data.tab === "knowledge" || data.tab === "rules") {
      api.learning.artifacts().then((d) => setData(p => ({...p, artifacts: unwrapList<ArtifactRow>(d, "artifacts")}))).catch(() => {});
      api.learning.rulesPending().then((d) => setData(p => ({...p, pendingRules: unwrapList<RuleRow>(d, "rules")}))).catch(() => {});
      api.learning.rulesApproved().then((d) => setData(p => ({...p, approvedRules: unwrapList<RuleRow>(d, "rules")}))).catch(() => {});
    }
  }, [data.tab]);

  const tabs = [
    { key: "failures" as const, label: "Failures", count: data.failures.length },
    { key: "lessons" as const, label: "Lessons", count: data.lessons.length },
    { key: "metrics" as const, label: "Metrics", count: data.metrics.length },
    { key: "proposals" as const, label: "Proposals", count: data.proposals.length },
    { key: "knowledge" as const, label: "Knowledge", count: data.artifacts.length },
    { key: "rules" as const, label: "Rules", count: data.pendingRules.length + data.approvedRules.length },
  ];

  function reviewProposal(id: string) {
    const note = proposalReview[id] || "";
    api.learning.reviewProposal(id, { decision: "approved", notes: note }).then(() => {
      api.learning.proposals().then((d) => setData(p => ({...p, proposals: Array.isArray(d) ? d : []}))).catch(() => {});
    }).catch(() => {});
  }

  function reviewRule(id: string, approved: boolean) {
    api.learning.reviewRule(id, approved).then(() => {
      api.learning.rulesPending().then((d) => setData(p => ({...p, pendingRules: unwrapList<RuleRow>(d, "rules")}))).catch(() => {});
      api.learning.rulesApproved().then((d) => setData(p => ({...p, approvedRules: unwrapList<RuleRow>(d, "rules")}))).catch(() => {});
    }).catch(() => {});
  }

  function doCreateLesson() {
    if (!createLesson.topic.trim() || !createLesson.description.trim()) return;
    api.learning.createLesson({ topic: createLesson.topic.trim(), description: createLesson.description.trim(), scope: createLesson.scope, evidence: [] }).then(() => {
      setCreateLesson({ show: false, topic: "", description: "", scope: "project" });
      api.learning.lessons("status=active").then((d) => setData(p => ({...p, lessons: Array.isArray(d) ? d : []}))).catch(() => {});
    }).catch(() => {});
  }

  return (
    <div className="space-y-8">
      <div className="animate-in">
        <h1 className="text-2xl font-bold tracking-tight">Learning System</h1>
        <p className="text-muted text-sm mt-1">Failure analysis, lessons, metrics, knowledge & improvements</p>
      </div>

      <div className="flex gap-2 border-b border-border pb-2 animate-in overflow-x-auto">
        {tabs.map((t) => (
          <button key={t.key} type="button" onClick={() => setData(p => ({...p, tab: t.key}))}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all whitespace-nowrap ${data.tab === t.key ? "bg-accent/10 text-accent" : "text-muted hover:text-foreground"}`}>
            {t.label} <span className="text-xs font-mono ml-1 opacity-60">{t.count}</span>
          </button>
        ))}
      </div>

      {data.tab === "failures" && (
        <div className="space-y-3 animate-in">
          <div className="bg-card border border-border rounded-xl p-5">
            <h2 className="text-sm font-semibold mb-3">5 Whys Analysis</h2>
            <div className="flex gap-2">
              <input value={why.input} onChange={(e) => setWhy(p => ({...p, input: e.target.value}))}
                placeholder="Paste problem description..." aria-label="Problem description"
                className="flex-1 bg-surface border border-border rounded-lg px-3 py-2 text-sm" />
              <button type="button" onClick={async () => { const r = await api.learning.fiveWhys(why.input); setWhy(p => ({...p, whys: r as unknown as WhyPair[]})); }}
                className="px-4 py-2 bg-accent text-black rounded-lg text-sm font-medium">Analyze</button>
            </div>
            {why.whys && (
              <div className="mt-3 space-y-1">{why.whys.map((w) => (
                <div key={w.question} className="flex gap-2 text-sm"><span className="text-accent font-mono shrink-0">{w.question}:</span><span>{w.answer}</span></div>
              ))}</div>
            )}
          </div>
          {!loaded ? <ListSkeleton rows={3} /> : data.failures.length === 0 ? (
            <p className="text-sm text-muted py-8 text-center">No failures recorded. Failures are logged automatically during task execution.</p>
          ) : data.failures.map((f) => (
            <div key={f.id ?? f.failure_id} className="bg-card border border-border rounded-xl p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-mono text-muted">{f.id ?? f.failure_id}</span>
                <span className={`px-2 py-0.5 rounded-full text-xs font-mono ${f.severity === "critical" ? "bg-red-500/10 text-red-500" : f.severity === "high" ? "bg-orange-500/10 text-orange-500" : "bg-yellow-500/10 text-yellow-500"}`}>{f.severity}</span>
              </div>
              <p className="text-sm font-medium">{f.description}</p>
              <p className="text-xs text-muted mt-1">Root cause: {f.root_cause}</p>
              {f.preventive_actions && f.preventive_actions.length > 0 && (
                <div className="mt-2 flex gap-1 flex-wrap">{f.preventive_actions.map((a) => (
                  <span key={a} className="px-2 py-0.5 bg-surface rounded text-xs text-muted">{a}</span>
                ))}</div>
              )}
            </div>
          ))}
        </div>
      )}

      {data.tab === "lessons" && (
        <div className="space-y-3 animate-in">
          <button type="button" onClick={() => setCreateLesson(c => ({...c, show: !c.show}))}
            className="px-4 py-2 bg-accent text-black rounded-lg text-sm font-medium">{createLesson.show ? "Cancel" : "+ New Lesson"}</button>
          {createLesson.show && (
            <div className="bg-card border border-border rounded-xl p-5 space-y-3">
              <input aria-label="Lesson topic" value={createLesson.topic} onChange={(e) => setCreateLesson(c => ({...c, topic: e.target.value}))}
                placeholder="Topic" className="w-full bg-surface border border-border rounded-lg px-3 py-2 text-sm" />
              <textarea aria-label="Lesson description" value={createLesson.description} onChange={(e) => setCreateLesson(c => ({...c, description: e.target.value}))}
                placeholder="Description" className="w-full bg-surface border border-border rounded-lg px-3 py-2 text-sm min-h-[60px]" />
              <select aria-label="Lesson scope" value={createLesson.scope} onChange={(e) => setCreateLesson(c => ({...c, scope: e.target.value}))}
                className="bg-surface border border-border rounded-lg px-3 py-2 text-sm">
                {["project", "project_type", "global"].map(s => <option key={s} value={s}>{s}</option>)}
              </select>
              <button type="button" onClick={doCreateLesson} disabled={!createLesson.topic.trim() || !createLesson.description.trim()}
                className="px-4 py-2 bg-accent text-black rounded-lg text-sm font-medium disabled:opacity-40">Create Lesson</button>
            </div>
          )}
          {!loaded ? <ListSkeleton rows={3} /> : data.lessons.length === 0 ? (
            <p className="text-sm text-muted py-8 text-center">No lessons recorded yet. Create your first lesson above.</p>
          ) : data.lessons.map((l) => (
            <div key={l.lesson_id} className="bg-card border border-border rounded-xl p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-mono text-muted">{l.lesson_id}</span>
                <div className="flex gap-2">
                  <span className="px-2 py-0.5 rounded text-xs font-mono bg-surface">{l.scope}</span>
                  <span className={`px-2 py-0.5 rounded text-xs font-mono ${l.confidence === "high" ? "bg-success/10 text-success" : "bg-yellow-500/10 text-yellow-500"}`}>{l.confidence}</span>
                </div>
              </div>
              <p className="text-sm font-medium">{l.topic}</p>
              <p className="text-xs text-muted mt-1">{l.description}</p>
            </div>
          ))}
        </div>
      )}

      {data.tab === "metrics" && (
        <div className="animate-in">
          {!loaded ? <ListSkeleton rows={2} /> : data.metrics.length === 0 ? <p className="text-sm text-muted py-8 text-center">No metrics recorded yet. Metrics are updated automatically during execution.</p> : (
            <div className="space-y-3">{data.metrics.slice().reverse().map((m) => (
              <div key={m.timestamp ?? m.id} className="bg-card border border-border rounded-xl p-4">
                <div className="text-xs font-mono text-muted mb-2">{m.timestamp}</div>
                <div className="text-2xl font-mono font-bold text-accent">{m.overall}</div>
                <div className="mt-2 flex flex-wrap gap-2">{Object.entries(m.categories as Record<string, string | number>).map(([k, v]) => (
                  <div key={k} className="text-xs"><span className="text-muted">{k}:</span> <span className="font-mono">{v}</span></div>
                ))}</div>
              </div>
            ))}</div>
          )}
        </div>
      )}

      {data.tab === "proposals" && (
        <div className="space-y-3 animate-in">
          {!loaded ? <ListSkeleton rows={3} /> : data.proposals.length === 0 && <p className="text-sm text-muted py-8 text-center">No improvement proposals yet.</p>}
          {data.proposals.map((p) => (
            <div key={p.proposal_id} className="bg-card border border-border rounded-xl p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-mono text-muted">{p.proposal_id}</span>
                <span className={`px-2 py-0.5 rounded-full text-xs font-mono ${p.status === "approved" ? "bg-success/10 text-success" : p.status === "rejected" ? "bg-red-500/10 text-red-500" : "bg-yellow-500/10 text-yellow-500"}`}>{p.status}</span>
              </div>
              <p className="text-sm font-medium">{p.observation}</p>
              <p className="text-xs text-muted mt-1">{p.expected_benefit}</p>
              {p.status === "pending" && (
                <div className="flex gap-2 mt-2">
                  <input aria-label="Proposal review notes" value={proposalReview[p.proposal_id as string] || ""} onChange={(e) => setProposalReview(r => ({...r, [p.proposal_id as string]: e.target.value}))}
                    placeholder="Review notes" className="flex-1 bg-surface border border-border rounded-lg px-3 py-1.5 text-xs" />
                  <button type="button" onClick={() => reviewProposal(p.proposal_id as string)}
                    className="px-3 py-1.5 bg-accent/10 text-accent rounded-lg text-xs font-medium">Review</button>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {data.tab === "knowledge" && (
        <div className="space-y-3 animate-in">
          <div className="bg-card border border-border rounded-xl p-5">
            <h2 className="text-sm font-semibold mb-3">Knowledge Artifacts ({data.artifacts.length})</h2>
            {data.artifacts.length === 0 ? <p className="text-xs text-muted">No knowledge artifacts.</p> : (
              <div className="divide-y divide-border">{data.artifacts.slice(0, 20).map((a) => (
                <div key={a.id || a.artifact_id} className="py-3 first:pt-0 last:pb-0">
                  <div className="text-sm font-medium">{a.title || a.topic}</div>
                  <div className="text-xs text-muted mt-0.5">{a.content?.slice(0, 200)}</div>
                </div>
              ))}</div>
            )}
          </div>
          <button type="button" onClick={() => api.learning.promoteKnowledge().then(() => api.learning.artifacts().then((d) => setData(p => ({...p, artifacts: Array.isArray(d) ? d : []})))).catch(() => {})}
            className="px-4 py-2 bg-surface border border-border rounded-lg text-sm">Promote Knowledge</button>
        </div>
      )}

      {data.tab === "rules" && (
        <div className="space-y-4 animate-in">
          {data.pendingRules.length > 0 && (
            <div className="bg-card border border-border rounded-xl p-5">
              <h2 className="text-sm font-semibold mb-3">Pending Review ({data.pendingRules.length})</h2>
              <div className="divide-y divide-border">{data.pendingRules.map((r) => (
                <div key={r.rule_id || r.id} className="py-3 first:pt-0 last:pb-0">
                  <p className="text-sm">{(r.description as string | undefined) || r.condition}</p>
                  <div className="flex gap-2 mt-2">
                    <button type="button" onClick={() => reviewRule((r.rule_id || r.id) as string, true)}
                      className="px-3 py-1 bg-success/10 text-success rounded-lg text-xs font-medium">Approve</button>
                    <button type="button" onClick={() => reviewRule((r.rule_id || r.id) as string, false)}
                      className="px-3 py-1 bg-red-500/10 text-red-500 rounded-lg text-xs font-medium">Reject</button>
                  </div>
                </div>
              ))}</div>
            </div>
          )}
          {data.approvedRules.length > 0 && (
            <div className="bg-card border border-border rounded-xl p-5">
              <h2 className="text-sm font-semibold mb-3">Approved Rules ({data.approvedRules.length})</h2>
              <div className="divide-y divide-border">{data.approvedRules.map((r) => (
                <div key={r.rule_id || r.id} className="py-3 first:pt-0 last:pb-0">
                  <p className="text-sm text-muted">{(r.description as string | undefined) || r.condition}</p>
                </div>
              ))}</div>
            </div>
          )}
          {!loaded ? <ListSkeleton rows={2} /> : data.pendingRules.length === 0 && data.approvedRules.length === 0 && (
            <p className="text-sm text-muted py-8 text-center">No rules yet. Rules are generated from learning outcomes.</p>
          )}
        </div>
      )}
    </div>
  );
}
