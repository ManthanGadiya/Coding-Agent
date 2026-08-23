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

export const api = {
  agents: {
    get: (id: string) => fetchJSON<unknown>(`/api/v1/agents/${id}`),
    status: (id: string) => fetchJSON<ManagerStatusResponse>(`/api/v1/agents/${id}/status`),
    runGoal: (goal: string, context?: Record<string, unknown>) =>
      fetchJSON<unknown>("/api/v1/agents/run-goal", { method: "POST", body: JSON.stringify({ goal, context }) }),
    registry: () => fetchJSON<unknown[]>("/api/v1/agents/registry/list"),
    conflictResolve: (data: Record<string, unknown>) => fetchJSON<unknown>("/api/v1/agents/conflict/resolve", { method: "POST", body: JSON.stringify(data) }),
    conflictHistory: () => fetchJSON<unknown[]>("/api/v1/agents/conflict/history"),
    disagreementResolve: (id: string, resolution: string) => fetchJSON<unknown>(`/api/v1/agents/disagreement/${id}/resolve`, { method: "POST", body: JSON.stringify({ resolution }) }),
    disagreementUnresolved: () => fetchJSON<unknown[]>("/api/v1/agents/disagreement/unresolved"),
  },

  manager: {
    status: () => fetchJSON<ManagerStatusResponse>("/api/v1/agents/manager/status"),
  },

  memory: {
    entries: (params?: string) => fetchJSON<unknown[]>(`/api/v1/memory/entries${params ? `?${params}` : ""}`),
    search: (q: string) => fetchJSON<unknown[]>(`/api/v1/memory/search?q=${encodeURIComponent(q)}`),
    stats: () => fetchJSON<Record<string, unknown>>("/api/v1/memory/stats", { quiet: true }).catch(() => null),
    createEntry: (data: Record<string, unknown>) => fetchJSON<unknown>("/api/v1/memory/entries", { method: "POST", body: JSON.stringify(data) }),
    deleteEntry: (id: string) => fetchJSON<unknown>(`/api/v1/memory/entries/${id}`, { method: "DELETE" }),
    versions: (id: string) => fetchJSON<unknown[]>(`/api/v1/memory/entries/${id}/versions`),
    compress: (entryIds: string[]) => fetchJSON<unknown>("/api/v1/memory/compress", { method: "POST", body: JSON.stringify({ entry_ids: entryIds }) }),
    suggestCompress: () => fetchJSON<unknown>("/api/v1/memory/compress/suggest", { method: "POST" }),
    stale: () => fetchJSON<unknown[]>("/api/v1/memory/retention/stale"),
    archivalCandidates: () => fetchJSON<unknown[]>("/api/v1/memory/retention/archival-candidates"),
    retentionHealth: () => fetchJSON<unknown>("/api/v1/memory/retention/health"),
  },

  learning: {
    failures: () => fetchJSON<unknown[]>("/api/v1/learning/failures"),
    lessons: (params?: string) => fetchJSON<unknown[]>(`/api/v1/learning/lessons${params ? `?${params}` : ""}`),
    metrics: () => fetchJSON<unknown[]>("/api/v1/learning/metrics"),
    proposals: () => fetchJSON<unknown[]>("/api/v1/learning/proposals"),
    fiveWhys: (problem: string) => fetchJSON<unknown>("/api/v1/learning/five-whys", { method: "POST", body: JSON.stringify({ problem }) }),
    createLesson: (data: Record<string, unknown>) => fetchJSON<unknown>("/api/v1/learning/lessons", { method: "POST", body: JSON.stringify(data) }),
    reviewProposal: (id: string, data: Record<string, unknown>) => fetchJSON<unknown>(`/api/v1/learning/proposals/${id}/review`, { method: "POST", body: JSON.stringify(data) }),
    promoteKnowledge: () => fetchJSON<unknown>("/api/v1/learning/knowledge/promote", { method: "POST" }),
    artifacts: () => fetchJSON<unknown[]>("/api/v1/learning/knowledge/artifacts"),
    rulesPending: () => fetchJSON<unknown[]>("/api/v1/learning/knowledge/rules/pending"),
    rulesApproved: () => fetchJSON<unknown[]>("/api/v1/learning/knowledge/rules/approved"),
    reviewRule: (id: string, approve: boolean) => fetchJSON<unknown>(`/api/v1/learning/knowledge/rules/${id}/review`, { method: "POST", body: JSON.stringify({ approve }) }),
  },

  memoryRetrieval: {
    retrieve: (data: Record<string, unknown>) => fetchJSON<unknown[]>("/api/v1/memory-retrieval/retrieve", { method: "POST", body: JSON.stringify(data) }),
    profiles: () => fetchJSON<Record<string, unknown>>("/api/v1/memory-retrieval/profiles"),
    profile: (agent: string) => fetchJSON<Record<string, unknown>>(`/api/v1/memory-retrieval/profile/${agent}`),
  },

  executor: {
    run: (name: string, context?: Record<string, unknown>) =>
      fetchJSON<unknown>("/api/v1/workflows/executor/run", { method: "POST", body: JSON.stringify({ name, context: context || {} }) }),
    instances: (status?: string) => fetchJSON<{instances: unknown[]}>(`/api/v1/workflows/executor/instances${status ? `?status=${status}` : ""}`),
    get: (id: string) => fetchJSON<unknown>(`/api/v1/workflows/executor/instances/${id}`),
    pause: (id: string) => fetchJSON<{status: string}>(`/api/v1/workflows/executor/instances/${id}/pause`, { method: "POST" }),
    resume: (id: string) => fetchJSON<{status: string}>(`/api/v1/workflows/executor/instances/${id}/resume`, { method: "POST" }),
    cancel: (id: string) => fetchJSON<{status: string}>(`/api/v1/workflows/executor/instances/${id}/cancel`, { method: "POST" }),
  },

  workflows: {
    list: () => fetchJSON<unknown[]>("/api/v1/workflows"),
    blueprint: (data: Record<string, unknown>) => fetchJSON<unknown>("/api/v1/workflows/blueprint", { method: "POST", body: JSON.stringify(data) }),
    classify: (data: Record<string, unknown>) => fetchJSON<unknown>("/api/v1/workflows/classify", { method: "POST", body: JSON.stringify(data) }),
    create: (data: Record<string, unknown>) => fetchJSON<unknown>("/api/v1/workflows", { method: "POST", body: JSON.stringify(data) }),
    categories: () => fetchJSON<{categories: string[]}>("/api/v1/workflows/categories"),
    get: (id: string) => fetchJSON<unknown>(`/api/v1/workflows/${id}`),
    execute: (id: string) => fetchJSON<unknown>(`/api/v1/workflows/${id}/execute`, { method: "POST" }),
    pause: (id: string) => fetchJSON<unknown>(`/api/v1/workflows/${id}/pause`, { method: "POST" }),
    resume: (id: string) => fetchJSON<unknown>(`/api/v1/workflows/${id}/resume`, { method: "POST" }),
    qualityGate: (checks: unknown[]) => fetchJSON<unknown>("/api/v1/workflows/quality-gate", { method: "POST", body: JSON.stringify({ checks }) }),
    recommend: (scope?: string, risk?: string) => fetchJSON<unknown>(`/api/v1/workflows/recommend?scope=${scope || "medium"}&risk=${risk || "low"}`),
  },

  autonomy: {
    mode: () => fetchJSON<{mode: string}>(`/api/v1/autonomy/mode`),
    setMode: (mode: string) => fetchJSON<{mode: string}>("/api/v1/autonomy/mode", { method: "POST", body: JSON.stringify({ mode }) }),
    check: (action: string, resource: string) =>
      fetchJSON<{allowed: boolean}>("/api/v1/autonomy/check", { method: "POST", body: JSON.stringify({ action, resource }) }),
  },

  llm: {
    models: () => fetchJSON<string[]>("/api/v1/llm/models"),
    select: (model: string) => fetchJSON<unknown>("/api/v1/llm/select", { method: "POST", body: JSON.stringify({ model }) }),
  },

  mcp: {
    servers: () => fetchJSON<unknown[]>("/api/v1/mcp/servers"),
    add: (name: string, config: Record<string, unknown>) =>
      fetchJSON<unknown>("/api/v1/mcp/servers", { method: "POST", body: JSON.stringify({ name, ...config }) }),
    remove: (name: string) => fetchJSON<unknown>(`/api/v1/mcp/servers/${encodeURIComponent(name)}`, { method: "DELETE" }),
    connect: (name: string) => fetchJSON<unknown>(`/api/v1/mcp/servers/${encodeURIComponent(name)}/connect`, { method: "POST" }),
    disconnect: (name: string) => fetchJSON<unknown>(`/api/v1/mcp/servers/${encodeURIComponent(name)}/disconnect`, { method: "POST" }),
  },

  tools: {
    list: () => fetchJSON<unknown[]>("/api/v1/tools/list"),
    execute: (name: string, args: Record<string, unknown>) =>
      fetchJSON<unknown>("/api/v1/tools/execute", { method: "POST", body: JSON.stringify({ name, args }) }),
  },

  skills: {
    list: () => fetchJSON<unknown[]>("/api/v1/skills/list"),
    execute: (name: string, args: Record<string, unknown>) =>
      fetchJSON<unknown>("/api/v1/skills/execute", { method: "POST", body: JSON.stringify({ name, args }) }),
  },

  projects: {
    list: () => fetchJSON<{ projects: unknown[]; total: number }>("/api/v1/projects"),
    create: (data: Record<string, unknown>) => fetchJSON<unknown>("/api/v1/projects", { method: "POST", body: JSON.stringify(data) }),
    get: (id: string) => fetchJSON<unknown>(`/api/v1/projects/${id}`),
    stats: (id: string) => fetchJSON<unknown>(`/api/v1/projects/${id}/stats`),
  },

  releases: {
    candidate: (version: string, release_type: string) =>
      fetchJSON<unknown>("/api/v1/workflows/release/candidate", { method: "POST", body: JSON.stringify({ version, release_type }) }),
    getCandidate: (id: string) => fetchJSON<unknown>(`/api/v1/workflows/release/candidate/${id}`),
    setCheck: (id: string, check_name: string, passed: boolean) =>
      fetchJSON<unknown>(`/api/v1/workflows/release/candidate/${id}/check?check_name=${encodeURIComponent(check_name)}&passed=${passed}`, { method: "POST" }),
    approve: (id: string, by: string) =>
      fetchJSON<unknown>(`/api/v1/workflows/release/candidate/${id}/approve?approved_by=${encodeURIComponent(by)}`, { method: "POST" }),
    deploy: (id: string) => fetchJSON<unknown>(`/api/v1/workflows/release/candidate/${id}/deploy`, { method: "POST" }),
    rollback: (id: string, reason?: string) =>
      fetchJSON<unknown>(`/api/v1/workflows/release/candidate/${id}/rollback${reason ? `?reason=${encodeURIComponent(reason)}` : ""}`, { method: "POST" }),
  },

  pipelines: {
    create: (category: string, complexity: string) =>
      fetchJSON<unknown>("/api/v1/workflows/pipeline", { method: "POST", body: JSON.stringify({ category, complexity }) }),
    get: (id: string) => fetchJSON<unknown>(`/api/v1/workflows/pipeline/${id}`),
    listActive: () => fetchJSON<{pipelines: unknown[]; count: number}>("/api/v1/workflows/pipeline/list/active"),
    transition: (id: string, status: string, output?: Record<string, unknown>) =>
      fetchJSON<unknown>(`/api/v1/workflows/pipeline/${id}/transition`, { method: "POST", body: JSON.stringify({ status, output: output || {} }) }),
    unblock: (id: string) => fetchJSON<unknown>(`/api/v1/workflows/pipeline/${id}/unblock`, { method: "POST" }),
    rollback: (id: string) => fetchJSON<unknown>(`/api/v1/workflows/pipeline/${id}/rollback`, { method: "POST" }),
  },

  decisions: {
    decide: (context: string, options: unknown[]) =>
      fetchJSON<unknown>("/api/v1/decisions/decide", { method: "POST", body: JSON.stringify({ context, options }) }),
    history: () => fetchJSON<unknown[]>("/api/v1/decisions/history"),
    assessRisk: (action: string) =>
      fetchJSON<unknown>("/api/v1/decisions/assess-risk", { method: "POST", body: JSON.stringify({ action }) }),
  },

  tasks: {
    list: (params?: string) => fetchJSON<TaskResponse[]>(`/api/v1/tasks${params ? `?${params}` : ""}`),
    create: (data: { title: string; description?: string; task_type?: string }) => fetchJSON<TaskResponse>("/api/v1/tasks", { method: "POST", body: JSON.stringify(data) }),
    update: (id: string, data: TaskUpdate) => fetchJSON<TaskResponse>(`/api/v1/tasks/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
  },

  users: {
    list: () => fetchJSON<{users: unknown[]}>("/api/v1/users"),
    create: (data: Record<string, unknown>) => fetchJSON<unknown>("/api/v1/users", { method: "POST", body: JSON.stringify(data) }),
    get: (id: string) => fetchJSON<unknown>(`/api/v1/users/${id}`),
    goals: (id: string) => fetchJSON<{goals: unknown[]}>(`/api/v1/users/${id}/goals`),
    createGoal: (id: string, data: Record<string, unknown>) => fetchJSON<unknown>(`/api/v1/users/${id}/goals`, { method: "POST", body: JSON.stringify(data) }),
    updateGoal: (userId: string, goalId: string, data: Record<string, unknown>) =>
      fetchJSON<unknown>(`/api/v1/users/${userId}/goals/${goalId}`, { method: "PATCH", body: JSON.stringify(data) }),
  },
};
