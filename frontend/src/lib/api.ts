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

export interface ProjectResponse {
  id: string; name: string; display_name: string; description?: string;
  status: string; repository_url?: string; local_path?: string;
  tech_stack?: string[]; architecture_decisions?: Record<string, unknown>[];
  constraints?: string[]; owner_id: string; settings?: Record<string, unknown>;
  task_count: number; completed_task_count: number;
  last_activity?: string; created_at: string; updated_at: string;
}
export interface ProjectListResponse { projects: ProjectResponse[]; total: number; page: number; page_size: number; }
export interface ProjectCreate { name: string; display_name?: string; description?: string; repository_url?: string; local_path?: string; tech_stack?: string[]; constraints?: string[]; }

export interface AgentResponse {
  id: string; agent_type: string; name: string; description?: string;
  status: string; capabilities: string[]; permissions: string[];
  current_task_id?: string; tasks_completed: number; tasks_failed: number;
  created_at: string; updated_at: string;
}
export interface AgentCreate { agent_type: string; name: string; description?: string; capabilities?: string[]; permissions?: string[]; }
export interface RunGoalRequest { goal: string; context?: Record<string, unknown>; }

export interface TaskResponse {
  id: string; title: string; description?: string; task_type: string;
  status: string; complexity: string; project_id?: string; parent_task_id?: string;
  assigned_agent?: string; workflow_id?: string; estimated_effort?: number;
  actual_effort?: number; started_at?: string; completed_at?: string;
  created_at: string; updated_at: string;
}
export interface TaskCreate { title: string; description?: string; task_type?: string; project_id?: string; estimated_effort?: number; }
export interface TaskUpdate { title?: string; description?: string; status?: string; assigned_agent?: string; estimated_effort?: number; actual_effort?: number; result?: string; error?: string; }

export interface MemoryEntryResponse {
  id: string; scope: string; project_id?: string; category: string;
  title: string; content: string; summary?: string; confidence: string;
  status: string; source_agent?: string; tags?: string[];
  usage_count: number; created_at: string; updated_at: string;
}
export interface MemoryEntryCreate { scope: string; project_id?: string; category: string; title: string; content: string; summary?: string; confidence?: string; source_agent?: string; tags?: string[]; }

export interface WorkflowResponse {
  id: string; name: string; description?: string; workflow_type: string;
  status: string; project_id?: string; steps: unknown[];
  current_step: number; total_steps: number; assigned_agents: unknown[];
  completed_agents: unknown[]; started_at?: string; completed_at?: string;
  created_at: string; updated_at: string;
}
export interface WorkflowCreate { name: string; description?: string; workflow_type?: string; project_id?: string; steps?: unknown[]; }

export interface RunGoalResponse { goal: string; classification: string; complexity: string; pipeline_id: string; pipeline_status: string; steps: { step: string; agent: string; status: string; task_type: string; output?: string; error?: string; }[]; success: boolean; total_steps: number; completed_steps: number; }
export interface ManagerStatusResponse { agent_id: string; name: string; state: string; capabilities: string[]; tasks_completed: number; tasks_failed: number; }

export interface FailureRecord { id: string; description: string; category: string; severity: string; root_cause: string; resolution: string; created_at: string; }
export interface LessonRecord { lesson_id: string; topic: string; description: string; confidence: string; scope: string; status: string; created_at: string; }
export interface LessonCreate { topic: string; description: string; evidence: string[]; confidence?: string; scope?: string; author?: string; }
export interface MetricSnapshot { id: string; overall: number; categories: Record<string, number>; created_at: string; }
export interface ImprovementProposal { id: string; observation: string; expected_benefit: string; recommendation: string; confidence: string; status: string; created_at: string; }

export interface MemoryRetrievalStore { content: string; tags?: string[]; importance?: number; confidence?: number; agent?: string; }
export interface MemoryRetrievalResult { id: string; content: string; tags: string[]; importance: number; confidence: number; agent: string; created_at: string; score: number; }

export const api = {
  health: () => fetchJSON<{ status: string }>("/health"),

  projects: {
    list: () => fetchJSON<ProjectListResponse>("/api/v1/projects"),
    get: (id: string) => fetchJSON<ProjectResponse>(`/api/v1/projects/${id}`),
    create: (data: ProjectCreate) => fetchJSON<ProjectResponse>("/api/v1/projects", { method: "POST", body: JSON.stringify(data) }),
    update: (id: string, data: Partial<ProjectCreate>) => fetchJSON<ProjectResponse>(`/api/v1/projects/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
    delete: (id: string) => fetchJSON<void>(`/api/v1/projects/${id}`, { method: "DELETE" }),
  },

  agents: {
    list: () => fetchJSON<AgentResponse[]>("/api/v1/agents"),
    get: (id: string) => fetchJSON<AgentResponse>(`/api/v1/agents/${id}`),
    create: (data: AgentCreate) => fetchJSON<AgentResponse>("/api/v1/agents", { method: "POST", body: JSON.stringify(data) }),
    update: (id: string, data: Partial<AgentCreate>) => fetchJSON<AgentResponse>(`/api/v1/agents/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
    delete: (id: string) => fetchJSON<void>(`/api/v1/agents/${id}`, { method: "DELETE" }),
    status: (id: string) => fetchJSON<ManagerStatusResponse>(`/api/v1/agents/${id}/status`),
    runGoal: (goal: string, context?: Record<string, unknown>) =>
      fetchJSON<RunGoalResponse>("/api/v1/agents/run-goal", { method: "POST", body: JSON.stringify({ goal, context }) }),
  },

  tasks: {
    list: (params?: string) => fetchJSON<TaskResponse[]>(`/api/v1/tasks${params ? `?${params}` : ""}`),
    get: (id: string) => fetchJSON<TaskResponse>(`/api/v1/tasks/${id}`),
    create: (data: TaskCreate) => fetchJSON<TaskResponse>("/api/v1/tasks", { method: "POST", body: JSON.stringify(data) }),
    update: (id: string, data: TaskUpdate) => fetchJSON<TaskResponse>(`/api/v1/tasks/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
    delete: (id: string) => fetchJSON<void>(`/api/v1/tasks/${id}`, { method: "DELETE" }),
  },

  memory: {
    entries: (params?: string) => fetchJSON<MemoryEntryResponse[]>(`/api/v1/memory/entries${params ? `?${params}` : ""}`),
    search: (q: string) => fetchJSON<MemoryEntryResponse[]>(`/api/v1/memory/search?q=${encodeURIComponent(q)}`),
    stats: () => fetchJSON<Record<string, unknown>>("/api/v1/memory/stats").catch(() => null),
  },

  manager: {
    status: () => fetchJSON<ManagerStatusResponse>("/api/v1/agents/manager/status"),
  },

  learning: {
    failures: () => fetchJSON<FailureRecord[]>("/api/v1/learning/failures"),
    recordFailure: (data: Record<string, unknown>) => fetchJSON<FailureRecord>("/api/v1/learning/failures", { method: "POST", body: JSON.stringify(data) }),
    lessons: (params?: string) => fetchJSON<LessonRecord[]>(`/api/v1/learning/lessons${params ? `?${params}` : ""}`),
    createLesson: (data: LessonCreate) => fetchJSON<LessonRecord>("/api/v1/learning/lessons", { method: "POST", body: JSON.stringify(data) }),
    metrics: () => fetchJSON<MetricSnapshot[]>("/api/v1/learning/metrics"),
    recordMetrics: (data: Record<string, unknown>) => fetchJSON<MetricSnapshot>("/api/v1/learning/metrics", { method: "POST", body: JSON.stringify(data) }),
    scoreMetrics: (data: Record<string, unknown>) => fetchJSON<Record<string, unknown>>("/api/v1/learning/metrics/score", { method: "POST", body: JSON.stringify(data) }),
    proposals: () => fetchJSON<ImprovementProposal[]>("/api/v1/learning/proposals"),
    propose: (data: Record<string, unknown>) => fetchJSON<ImprovementProposal>("/api/v1/learning/proposals", { method: "POST", body: JSON.stringify(data) }),
    fiveWhys: (problem: string) => fetchJSON<Record<string, unknown>>("/api/v1/learning/five-whys", { method: "POST", body: JSON.stringify({ problem }) }),
  },

  memoryRetrieval: {
    store: (data: MemoryRetrievalStore) => fetchJSON<MemoryRetrievalResult>("/api/v1/memory-retrieval/store", { method: "POST", body: JSON.stringify(data) }),
    retrieve: (data: Record<string, unknown>) => fetchJSON<MemoryRetrievalResult[]>("/api/v1/memory-retrieval/retrieve", { method: "POST", body: JSON.stringify(data) }),
    expand: (data: Record<string, unknown>) => fetchJSON<MemoryRetrievalResult[]>("/api/v1/memory-retrieval/expand", { method: "POST", body: JSON.stringify(data) }),
    profiles: () => fetchJSON<Record<string, unknown>>("/api/v1/memory-retrieval/profiles"),
    profile: (agent: string) => fetchJSON<Record<string, unknown>>(`/api/v1/memory-retrieval/profile/${agent}`),
  },

  workflows: {
    list: () => fetchJSON<WorkflowResponse[]>("/api/v1/workflows"),
    get: (id: string) => fetchJSON<WorkflowResponse>(`/api/v1/workflows/${id}`),
    create: (data: WorkflowCreate) => fetchJSON<WorkflowResponse>("/api/v1/workflows", { method: "POST", body: JSON.stringify(data) }),
    blueprint: (data: Record<string, unknown>) => fetchJSON<Record<string, unknown>>("/api/v1/workflows/blueprint", { method: "POST", body: JSON.stringify(data) }),
    classify: (data: Record<string, unknown>) => fetchJSON<Record<string, unknown>>("/api/v1/workflows/classify", { method: "POST", body: JSON.stringify(data) }),
    categories: () => fetchJSON<string[]>("/api/v1/workflows/categories"),
  },
};
