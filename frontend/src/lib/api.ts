const BASE = "";

async function fetchJSON<T>(url: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${url}`, {
    headers: { "Content-Type": "application/json", ...init?.headers },
    ...init,
  });
  if (!res.ok) {
    const err = await res.text();
    throw new Error(`${res.status} ${res.statusText}: ${err.slice(0, 200)}`);
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
  projects: {
    list: () => fetchJSON<{ projects: unknown[]; total: number }>("/api/v1/projects"),
    create: (data: Record<string, unknown>) => fetchJSON<unknown>("/api/v1/projects", { method: "POST", body: JSON.stringify(data) }),
  },

  agents: {
    get: (id: string) => fetchJSON<unknown>(`/api/v1/agents/${id}`),
    status: (id: string) => fetchJSON<ManagerStatusResponse>(`/api/v1/agents/${id}/status`),
    runGoal: (goal: string, context?: Record<string, unknown>) =>
      fetchJSON<unknown>("/api/v1/agents/run-goal", { method: "POST", body: JSON.stringify({ goal, context }) }),
  },

  tasks: {
    list: (params?: string) => fetchJSON<TaskResponse[]>(`/api/v1/tasks${params ? `?${params}` : ""}`),
    create: (data: { title: string; description?: string; task_type?: string }) => fetchJSON<TaskResponse>("/api/v1/tasks", { method: "POST", body: JSON.stringify(data) }),
    update: (id: string, data: TaskUpdate) => fetchJSON<TaskResponse>(`/api/v1/tasks/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
  },

  memory: {
    entries: (params?: string) => fetchJSON<unknown[]>(`/api/v1/memory/entries${params ? `?${params}` : ""}`),
    search: (q: string) => fetchJSON<unknown[]>(`/api/v1/memory/search?q=${encodeURIComponent(q)}`),
    stats: () => fetchJSON<Record<string, unknown>>("/api/v1/memory/stats").catch(() => null),
  },

  manager: {
    status: () => fetchJSON<ManagerStatusResponse>("/api/v1/agents/manager/status"),
  },

  learning: {
    failures: () => fetchJSON<unknown[]>("/api/v1/learning/failures"),
    lessons: (params?: string) => fetchJSON<unknown[]>(`/api/v1/learning/lessons${params ? `?${params}` : ""}`),
    metrics: () => fetchJSON<unknown[]>("/api/v1/learning/metrics"),
    proposals: () => fetchJSON<unknown[]>("/api/v1/learning/proposals"),
    fiveWhys: (problem: string) => fetchJSON<unknown>("/api/v1/learning/five-whys", { method: "POST", body: JSON.stringify({ problem }) }),
  },

  memoryRetrieval: {
    retrieve: (data: Record<string, unknown>) => fetchJSON<unknown[]>("/api/v1/memory-retrieval/retrieve", { method: "POST", body: JSON.stringify(data) }),
    profiles: () => fetchJSON<Record<string, unknown>>("/api/v1/memory-retrieval/profiles"),
    profile: (agent: string) => fetchJSON<Record<string, unknown>>(`/api/v1/memory-retrieval/profile/${agent}`),
  },

  workflows: {
    list: () => fetchJSON<unknown[]>("/api/v1/workflows"),
    blueprint: (data: Record<string, unknown>) => fetchJSON<unknown>("/api/v1/workflows/blueprint", { method: "POST", body: JSON.stringify(data) }),
    classify: (data: Record<string, unknown>) => fetchJSON<unknown>("/api/v1/workflows/classify", { method: "POST", body: JSON.stringify(data) }),
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
};
