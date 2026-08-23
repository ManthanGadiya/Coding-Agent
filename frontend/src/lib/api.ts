const BASE = "";

type ApiErrorListener = (message: string) => void;
const errorListeners = new Set<ApiErrorListener>();

export function onApiError(listener: ApiErrorListener): () => void {
  errorListeners.add(listener);
  return () => { errorListeners.delete(listener); };
}

function reportApiError(message: string): void {
  errorListeners.forEach((listener) => listener(message));
}

async function fetchJSON<T>(url: string, init?: RequestInit & { quiet?: boolean }): Promise<T> {
  let res: Response;
  try {
    res = await fetch(`${BASE}${url}`, {
      headers: { "Content-Type": "application/json", ...init?.headers },
      ...init,
    });
  } catch {
    if (!init?.quiet) {
      reportApiError(`Cannot reach API (${url}) — is the backend running on port 8000?`);
    }
    throw new Error(`Network error calling ${url}`);
  }
  if (!res.ok) {
    const err = await res.text();
    const message = `${res.status} ${res.statusText}: ${err.slice(0, 200)}`;
    if (!init?.quiet && res.status >= 500) reportApiError(`${message} (${url})`);
    throw new Error(message);
  }
  if (res.status === 204) return null as unknown as T;
  return res.json();
}

export interface TaskResponse {
  id: string; title: string; description?: string; task_type: string;
  status: string; complexity: string; project_id?: string; parent_task_id?: string;
  assigned_agent?: string; workflow_id?: string; estimated_effort?: number;
  actual_effort?: number; started_at?: string; completed_at?: string;
  created_at: string; updated_at: string;
}
export interface TaskUpdate { title?: string; description?: string; status?: string; assigned_agent?: string; estimated_effort?: number; actual_effort?: number; result?: string; error?: string; }

export interface ManagerStatusResponse { agent_id: string; name: string; state: string; capabilities: string[]; tasks_completed: number; tasks_failed: number; }

/* ---- shared shape helper: declared fields are typed, everything else stays accessible ---- */
interface ApiObject {
  [key: string]: unknown;
}

export interface AgentInfo extends ApiObject {
  agent_id?: string; id?: string; name?: string; description?: string;
  agent_type?: string; state?: string; capabilities?: string[];
  tasks_completed?: number; tasks_failed?: number; created_at?: string;
}

export interface RegistryEntry extends ApiObject {
  agent_type?: string; name?: string; description?: string; capabilities?: string[];
}

export interface ConflictRecord extends ApiObject {
  id?: string; agent_a?: string; agent_b?: string; conflict_type?: string;
  resolution?: string; resolved_by?: string; status?: string; created_at?: string;
}

export interface DisagreementRecord extends ApiObject {
  id?: string; level?: string; topic?: string; status?: string;
  raised_by?: string; resolution?: string; created_at?: string;
}

export interface MemoryEntry extends ApiObject {
  id?: string; scope?: string; project_id?: string; category?: string;
  key?: string; value?: string; title?: string; content?: string; summary?: string;
  confidence?: string; status?: string; source_agent?: string; evidence?: string;
  tags?: string[]; related_entries?: string[]; usage_count?: number;
  last_accessed?: string; created_at?: string; updated_at?: string;
}

export interface MemoryVersion extends ApiObject {
  version?: number; content?: string; changed_by?: string; created_at?: string;
}

export interface RetentionCandidate extends ApiObject {
  id?: string; title?: string; reason?: string; score?: number; stale_days?: number;
}

export interface RetentionHealth extends ApiObject {
  total_active?: number; healthy?: boolean; stale_count?: number;
  archival_candidates?: number; average_retention_score?: number;
}

export interface CompressionSuggestion extends ApiObject {
  suggested_entries?: string[]; reason?: string; potential_savings?: number;
}

export interface LearningFailure extends ApiObject {
  id?: string; failure_type?: string; severity?: string; description?: string;
  context?: string; root_cause?: string; detected_by?: string; created_at?: string;
}

export interface Lesson extends ApiObject {
  id?: string; title?: string; lesson?: string; content?: string;
  scope?: string; status?: string; confidence?: string;
  source_failure_id?: string; times_applied?: number; created_at?: string;
}

export interface LearningMetric extends ApiObject {
  id?: string; metric_name?: string; name?: string; value?: number;
  unit?: string; period?: string; recorded_at?: string;
}

export interface ImprovementProposal extends ApiObject {
  id?: string; title?: string; proposal?: string; rationale?: string;
  status?: string; priority?: string; created_at?: string;
}

export interface KnowledgeArtifact extends ApiObject {
  id?: string; artifact_type?: string; title?: string; content?: string;
  confidence?: string; source_observations?: number; promoted?: boolean; created_at?: string;
}

export interface CandidateRule extends ApiObject {
  id?: string; rule?: string; condition?: string; action?: string;
  confidence?: number; status?: string; observation_count?: number; created_at?: string;
}

export interface RetrievalResult extends ApiObject {
  entry_id?: string; id?: string; score?: number; relevance_score?: number;
  title?: string; content?: string; category?: string; matched_factors?: string[];
}

export interface RetrieveResponse extends ApiObject {
  memories?: RetrievalResult[]; summary?: string; confidence?: number;
  contradictions?: unknown[];
}

export interface AgentProfile extends ApiObject {
  profile?: Record<string, unknown>; agent_type?: string; weights?: Record<string, number>;
}

export interface WorkflowDef extends ApiObject {
  id?: string; name?: string; workflow_type?: string; category?: string;
  complexity?: string; status?: string; steps?: WorkflowStep[];
  description?: string; created_at?: string;
}

export interface WorkflowStep extends ApiObject {
  name?: string; step_type?: string; agent_role?: string; order?: number; config?: Record<string, unknown>;
}

export interface ExecutorInstance extends ApiObject {
  instance_id?: string; id?: string; workflow_name?: string; blueprint?: string;
  status?: string; current_step?: string; progress?: number;
  started_at?: string; completed_at?: string; error?: string;
}

export interface ToolDef extends ApiObject {
  name?: string; description?: string; risk_level?: string;
  parameters?: Record<string, unknown>; required_permissions?: string[];
}

export interface SkillDef extends ApiObject {
  name?: string; description?: string; version?: string;
}

export interface Project extends ApiObject {
  id?: string; name?: string; display_name?: string; description?: string;
  status?: string; goals?: UserGoal[]; created_at?: string; updated_at?: string;
}

export interface ProjectStats extends ApiObject {
  total_tasks?: number; completed_tasks?: number; active_tasks?: number;
  completion_rate?: number; team_size?: number;
}

export interface ReleaseCandidate extends ApiObject {
  id?: string; version?: string; release_type?: string; state?: string; status?: string;
  checks?: Record<string, boolean>; approved_by?: string; strategy?: string;
  deployed_at?: string; created_at?: string;
}

export interface PipelineInstance extends ApiObject {
  id?: string; category?: string; complexity?: string; status?: string;
  current_stage?: string; history?: Array<Record<string, unknown>>;
  blocked_reason?: string; created_at?: string; updated_at?: string;
}

export interface DecisionRecord extends ApiObject {
  id?: string; context?: string; decision?: string; chosen_option?: string;
  options?: unknown[]; confidence?: number; rationale?: string; created_at?: string;
}

export interface RiskAssessment extends ApiObject {
  action?: string; risk_level?: string; score?: number; factors?: string[];
  recommendation?: string;
}

export interface UserRecord extends ApiObject {
  id?: string; username?: string; name?: string; email?: string;
  display_name?: string; role?: string; preferences?: Record<string, unknown>; created_at?: string;
}

export interface UserGoal extends ApiObject {
  id?: string; user_id?: string; goal?: string; title?: string; description?: string;
  priority?: string; status?: string; target_date?: string; created_at?: string;
}

export interface MCPServer extends ApiObject {
  name?: string; command?: string; url?: string; status?: string;
  connected?: boolean; tool_count?: number; transport?: string;
}

export type { ApiObject };

export const api = {
  agents: {
    get: (id: string) => fetchJSON<AgentInfo>(`/api/v1/agents/${id}`),
    status: (id: string) => fetchJSON<ManagerStatusResponse>(`/api/v1/agents/${id}/status`),
    runGoal: (goal: string, context?: Record<string, unknown>) =>
      fetchJSON<Record<string, unknown>>("/api/v1/agents/run-goal", { method: "POST", body: JSON.stringify({ goal, context }) }),
    registry: () => fetchJSON<RegistryEntry[]>("/api/v1/agents/registry/list"),
    conflictResolve: (data: Record<string, unknown>) => fetchJSON<Record<string, unknown>>("/api/v1/agents/conflict/resolve", { method: "POST", body: JSON.stringify(data) }),
    conflictHistory: () => fetchJSON<ConflictRecord[]>("/api/v1/agents/conflict/history"),
    disagreementResolve: (id: string, resolution: string) => fetchJSON<Record<string, unknown>>(`/api/v1/agents/disagreement/${id}/resolve`, { method: "POST", body: JSON.stringify({ resolution }) }),
    disagreementUnresolved: () => fetchJSON<DisagreementRecord[]>("/api/v1/agents/disagreement/unresolved"),
  },

  manager: {
    status: () => fetchJSON<ManagerStatusResponse>("/api/v1/agents/manager/status"),
  },

  memory: {
    entries: (params?: string) => fetchJSON<MemoryEntry[]>(`/api/v1/memory/entries${params ? `?${params}` : ""}`),
    search: (q: string) => fetchJSON<MemoryEntry[]>(`/api/v1/memory/search?q=${encodeURIComponent(q)}`),
    stats: () => fetchJSON<Record<string, unknown>>("/api/v1/memory/stats", { quiet: true }).catch(() => null),
    createEntry: (data: Record<string, unknown>) => fetchJSON<MemoryEntry>("/api/v1/memory/entries", { method: "POST", body: JSON.stringify(data) }),
    deleteEntry: (id: string) => fetchJSON<void>(`/api/v1/memory/entries/${id}`, { method: "DELETE" }),
    versions: (id: string) => fetchJSON<MemoryVersion[]>(`/api/v1/memory/entries/${id}/versions`),
    compress: (entryIds: string[]) => fetchJSON<Record<string, unknown>>("/api/v1/memory/compress", { method: "POST", body: JSON.stringify({ entry_ids: entryIds }) }),
    suggestCompress: () => fetchJSON<CompressionSuggestion>("/api/v1/memory/compress/suggest", { method: "POST" }),
    stale: () => fetchJSON<RetentionCandidate[]>("/api/v1/memory/retention/stale"),
    archivalCandidates: () => fetchJSON<RetentionCandidate[]>("/api/v1/memory/retention/archival-candidates"),
    retentionHealth: () => fetchJSON<RetentionHealth>("/api/v1/memory/retention/health"),
  },

  learning: {
    failures: () => fetchJSON<LearningFailure[]>("/api/v1/learning/failures"),
    lessons: (params?: string) => fetchJSON<Lesson[]>(`/api/v1/learning/lessons${params ? `?${params}` : ""}`),
    metrics: () => fetchJSON<LearningMetric[]>("/api/v1/learning/metrics"),
    proposals: () => fetchJSON<ImprovementProposal[]>("/api/v1/learning/proposals"),
    fiveWhys: (problem: string) => fetchJSON<Record<string, unknown>>("/api/v1/learning/five-whys", { method: "POST", body: JSON.stringify({ problem }) }),
    createLesson: (data: Record<string, unknown>) => fetchJSON<Lesson>("/api/v1/learning/lessons", { method: "POST", body: JSON.stringify(data) }),
    reviewProposal: (id: string, data: Record<string, unknown>) => fetchJSON<ImprovementProposal>(`/api/v1/learning/proposals/${id}/review`, { method: "POST", body: JSON.stringify(data) }),
    promoteKnowledge: () => fetchJSON<Record<string, unknown>>("/api/v1/learning/knowledge/promote", { method: "POST" }),
    artifacts: () => fetchJSON<KnowledgeArtifact[]>("/api/v1/learning/knowledge/artifacts"),
    rulesPending: () => fetchJSON<CandidateRule[]>("/api/v1/learning/knowledge/rules/pending"),
    rulesApproved: () => fetchJSON<CandidateRule[]>("/api/v1/learning/knowledge/rules/approved"),
    reviewRule: (id: string, approve: boolean) => fetchJSON<CandidateRule>(`/api/v1/learning/knowledge/rules/${id}/review`, { method: "POST", body: JSON.stringify({ approve }) }),
  },

  memoryRetrieval: {
    retrieve: (data: Record<string, unknown>) => fetchJSON<RetrieveResponse>("/api/v1/memory-retrieval/retrieve", { method: "POST", body: JSON.stringify(data) }),
    profiles: () => fetchJSON<Record<string, AgentProfile>>("/api/v1/memory-retrieval/profiles"),
    profile: (agent: string) => fetchJSON<AgentProfile>(`/api/v1/memory-retrieval/profile/${agent}`),
  },

  executor: {
    run: (name: string, context?: Record<string, unknown>) =>
      fetchJSON<ExecutorInstance>("/api/v1/workflows/executor/run", { method: "POST", body: JSON.stringify({ name, context: context || {} }) }),
    instances: (status?: string) => fetchJSON<{instances: ExecutorInstance[]}>(`/api/v1/workflows/executor/instances${status ? `?status=${status}` : ""}`),
    get: (id: string) => fetchJSON<ExecutorInstance>(`/api/v1/workflows/executor/instances/${id}`),
    pause: (id: string) => fetchJSON<{status: string}>(`/api/v1/workflows/executor/instances/${id}/pause`, { method: "POST" }),
    resume: (id: string) => fetchJSON<{status: string}>(`/api/v1/workflows/executor/instances/${id}/resume`, { method: "POST" }),
    cancel: (id: string) => fetchJSON<{status: string}>(`/api/v1/workflows/executor/instances/${id}/cancel`, { method: "POST" }),
  },

  workflows: {
    list: () => fetchJSON<WorkflowDef[]>("/api/v1/workflows"),
    blueprint: (data: Record<string, unknown>) => fetchJSON<WorkflowDef>("/api/v1/workflows/blueprint", { method: "POST", body: JSON.stringify(data) }),
    classify: (data: Record<string, unknown>) => fetchJSON<Record<string, unknown>>("/api/v1/workflows/classify", { method: "POST", body: JSON.stringify(data) }),
    create: (data: Record<string, unknown>) => fetchJSON<WorkflowDef>("/api/v1/workflows", { method: "POST", body: JSON.stringify(data) }),
    categories: () => fetchJSON<{categories: string[]}>("/api/v1/workflows/categories"),
    get: (id: string) => fetchJSON<WorkflowDef>(`/api/v1/workflows/${id}`),
    execute: (id: string) => fetchJSON<Record<string, unknown>>(`/api/v1/workflows/${id}/execute`, { method: "POST" }),
    pause: (id: string) => fetchJSON<WorkflowDef>(`/api/v1/workflows/${id}/pause`, { method: "POST" }),
    resume: (id: string) => fetchJSON<WorkflowDef>(`/api/v1/workflows/${id}/resume`, { method: "POST" }),
    qualityGate: (checks: unknown[]) => fetchJSON<Record<string, unknown>>("/api/v1/workflows/quality-gate", { method: "POST", body: JSON.stringify({ checks }) }),
    recommend: (scope?: string, risk?: string) => fetchJSON<Record<string, unknown>>(`/api/v1/workflows/recommend?scope=${scope || "medium"}&risk=${risk || "low"}`),
  },

  autonomy: {
    mode: () => fetchJSON<{mode: string}>(`/api/v1/autonomy/mode`),
    setMode: (mode: string) => fetchJSON<{mode: string}>("/api/v1/autonomy/mode", { method: "POST", body: JSON.stringify({ mode }) }),
    check: (action: string, resource: string) =>
      fetchJSON<{allowed: boolean}>("/api/v1/autonomy/check", { method: "POST", body: JSON.stringify({ action, resource }) }),
  },

  llm: {
    models: () => fetchJSON<string[]>("/api/v1/llm/models"),
    select: (model: string) => fetchJSON<{selected?: string}>("/api/v1/llm/select", { method: "POST", body: JSON.stringify({ model }) }),
  },

  mcp: {
    servers: () => fetchJSON<MCPServer[]>("/api/v1/mcp/servers"),
    add: (name: string, config: Record<string, unknown>) =>
      fetchJSON<MCPServer>("/api/v1/mcp/servers", { method: "POST", body: JSON.stringify({ name, ...config }) }),
    remove: (name: string) => fetchJSON<void>(`/api/v1/mcp/servers/${encodeURIComponent(name)}`, { method: "DELETE" }),
    connect: (name: string) => fetchJSON<MCPServer>(`/api/v1/mcp/servers/${encodeURIComponent(name)}/connect`, { method: "POST" }),
    disconnect: (name: string) => fetchJSON<MCPServer>(`/api/v1/mcp/servers/${encodeURIComponent(name)}/disconnect`, { method: "POST" }),
  },

  tools: {
    list: () => fetchJSON<ToolDef[]>("/api/v1/tools/list"),
    execute: (name: string, args: Record<string, unknown>) =>
      fetchJSON<Record<string, unknown>>("/api/v1/tools/execute", { method: "POST", body: JSON.stringify({ name, args }) }),
  },

  skills: {
    list: () => fetchJSON<SkillDef[]>("/api/v1/skills/list"),
    execute: (name: string, args: Record<string, unknown>) =>
      fetchJSON<Record<string, unknown>>("/api/v1/skills/execute", { method: "POST", body: JSON.stringify({ name, args }) }),
  },

  projects: {
    list: () => fetchJSON<{ projects: Project[]; total: number }>("/api/v1/projects"),
    create: (data: Record<string, unknown>) => fetchJSON<Project>("/api/v1/projects", { method: "POST", body: JSON.stringify(data) }),
    get: (id: string) => fetchJSON<Project>(`/api/v1/projects/${id}`),
    stats: (id: string) => fetchJSON<ProjectStats>(`/api/v1/projects/${id}/stats`),
  },

  releases: {
    candidate: (version: string, release_type: string) =>
      fetchJSON<ReleaseCandidate>("/api/v1/workflows/release/candidate", { method: "POST", body: JSON.stringify({ version, release_type }) }),
    getCandidate: (id: string) => fetchJSON<ReleaseCandidate>(`/api/v1/workflows/release/candidate/${id}`),
    setCheck: (id: string, check_name: string, passed: boolean) =>
      fetchJSON<ReleaseCandidate>(`/api/v1/workflows/release/candidate/${id}/check?check_name=${encodeURIComponent(check_name)}&passed=${passed}`, { method: "POST" }),
    approve: (id: string, by: string) =>
      fetchJSON<ReleaseCandidate>(`/api/v1/workflows/release/candidate/${id}/approve?approved_by=${encodeURIComponent(by)}`, { method: "POST" }),
    deploy: (id: string) => fetchJSON<ReleaseCandidate>(`/api/v1/workflows/release/candidate/${id}/deploy`, { method: "POST" }),
    rollback: (id: string, reason?: string) =>
      fetchJSON<ReleaseCandidate>(`/api/v1/workflows/release/candidate/${id}/rollback${reason ? `?reason=${encodeURIComponent(reason)}` : ""}`, { method: "POST" }),
  },

  pipelines: {
    create: (category: string, complexity: string) =>
      fetchJSON<PipelineInstance>("/api/v1/workflows/pipeline", { method: "POST", body: JSON.stringify({ category, complexity }) }),
    get: (id: string) => fetchJSON<PipelineInstance>(`/api/v1/workflows/pipeline/${id}`),
    listActive: () => fetchJSON<{pipelines: PipelineInstance[]; count: number}>("/api/v1/workflows/pipeline/list/active"),
    transition: (id: string, status: string, output?: Record<string, unknown>) =>
      fetchJSON<PipelineInstance>(`/api/v1/workflows/pipeline/${id}/transition`, { method: "POST", body: JSON.stringify({ status, output: output || {} }) }),
    unblock: (id: string) => fetchJSON<PipelineInstance>(`/api/v1/workflows/pipeline/${id}/unblock`, { method: "POST" }),
    rollback: (id: string) => fetchJSON<PipelineInstance>(`/api/v1/workflows/pipeline/${id}/rollback`, { method: "POST" }),
  },

  decisions: {
    decide: (context: string, options: unknown[]) =>
      fetchJSON<DecisionRecord>("/api/v1/decisions/decide", { method: "POST", body: JSON.stringify({ context, options }) }),
    history: () => fetchJSON<DecisionRecord[]>("/api/v1/decisions/history"),
    assessRisk: (action: string) =>
      fetchJSON<RiskAssessment>("/api/v1/decisions/assess-risk", { method: "POST", body: JSON.stringify({ action }) }),
  },

  tasks: {
    list: (params?: string) => fetchJSON<TaskResponse[]>(`/api/v1/tasks${params ? `?${params}` : ""}`),
    create: (data: { title: string; description?: string; task_type?: string }) => fetchJSON<TaskResponse>("/api/v1/tasks", { method: "POST", body: JSON.stringify(data) }),
    update: (id: string, data: TaskUpdate) => fetchJSON<TaskResponse>(`/api/v1/tasks/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
  },

  users: {
    list: () => fetchJSON<{users: UserRecord[]}>("/api/v1/users"),
    create: (data: Record<string, unknown>) => fetchJSON<UserRecord>("/api/v1/users", { method: "POST", body: JSON.stringify(data) }),
    get: (id: string) => fetchJSON<UserRecord>(`/api/v1/users/${id}`),
    goals: (id: string) => fetchJSON<{goals: UserGoal[]}>(`/api/v1/users/${id}/goals`),
    createGoal: (id: string, data: Record<string, unknown>) => fetchJSON<UserGoal>(`/api/v1/users/${id}/goals`, { method: "POST", body: JSON.stringify(data) }),
    updateGoal: (userId: string, goalId: string, data: Record<string, unknown>) =>
      fetchJSON<UserGoal>(`/api/v1/users/${userId}/goals/${goalId}`, { method: "PATCH", body: JSON.stringify(data) }),
  },
};
