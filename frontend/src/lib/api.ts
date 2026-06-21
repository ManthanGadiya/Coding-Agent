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
  return res.json();
}

export const api = {
  health: () => fetchJSON<{ status: string }>("/health"),

  projects: {
    list: () => fetchJSON<any[]>("/api/v1/projects"),
    get: (id: string) => fetchJSON<any>(`/api/v1/projects/${id}`),
    create: (data: any) => fetchJSON<any>("/api/v1/projects", { method: "POST", body: JSON.stringify(data) }),
  },

  agents: {
    list: () => fetchJSON<any[]>("/api/v1/agents"),
    get: (id: string) => fetchJSON<any>(`/api/v1/agents/${id}`),
    status: (id: string) => fetchJSON<any>(`/api/v1/agents/${id}/status`),
  },

  tasks: {
    list: (params?: string) => fetchJSON<any[]>(`/api/v1/tasks${params ? `?${params}` : ""}`),
    get: (id: string) => fetchJSON<any>(`/api/v1/tasks/${id}`),
    create: (data: any) => fetchJSON<any>("/api/v1/tasks", { method: "POST", body: JSON.stringify(data) }),
  },

  memory: {
    entries: (params?: string) => fetchJSON<any[]>(`/api/v1/memory/entries${params ? `?${params}` : ""}`),
    search: (q: string) => fetchJSON<any[]>(`/api/v1/memory/search?q=${encodeURIComponent(q)}`),
  },

  manager: {
    status: () => fetchJSON<any>("/api/v1/agents/manager/status"),
  },
  orchestrator: {
    status: () => fetchJSON<any>("/api/v1/agents/manager/status"),
  },

  learning: {
    failures: () => fetchJSON<any[]>("/api/v1/learning/failures"),
    recordFailure: (data: any) => fetchJSON<any>("/api/v1/learning/failures", { method: "POST", body: JSON.stringify(data) }),
    lessons: (params?: string) => fetchJSON<any[]>(`/api/v1/learning/lessons${params ? `?${params}` : ""}`),
    createLesson: (data: any) => fetchJSON<any>("/api/v1/learning/lessons", { method: "POST", body: JSON.stringify(data) }),
    metrics: () => fetchJSON<any[]>("/api/v1/learning/metrics"),
    recordMetrics: (data: any) => fetchJSON<any>("/api/v1/learning/metrics", { method: "POST", body: JSON.stringify(data) }),
    scoreMetrics: (data: any) => fetchJSON<any>("/api/v1/learning/metrics/score", { method: "POST", body: JSON.stringify(data) }),
    proposals: () => fetchJSON<any[]>("/api/v1/learning/proposals"),
    propose: (data: any) => fetchJSON<any>("/api/v1/learning/proposals", { method: "POST", body: JSON.stringify(data) }),
    fiveWhys: (problem: string) => fetchJSON<any>("/api/v1/learning/five-whys", { method: "POST", body: JSON.stringify({ problem }) }),
  },

  memoryRetrieval: {
    store: (data: any) => fetchJSON<any>("/api/v1/memory-retrieval/store", { method: "POST", body: JSON.stringify(data) }),
    retrieve: (data: any) => fetchJSON<any>("/api/v1/memory-retrieval/retrieve", { method: "POST", body: JSON.stringify(data) }),
    expand: (data: any) => fetchJSON<any>("/api/v1/memory-retrieval/expand", { method: "POST", body: JSON.stringify(data) }),
    profiles: () => fetchJSON<any>("/api/v1/memory-retrieval/profiles"),
    profile: (agent: string) => fetchJSON<any>(`/api/v1/memory-retrieval/profile/${agent}`),
  },

  workflows: {
    list: () => fetchJSON<any[]>("/api/v1/workflows"),
    get: (id: string) => fetchJSON<any>(`/api/v1/workflows/${id}`),
    create: (data: any) => fetchJSON<any>("/api/v1/workflows", { method: "POST", body: JSON.stringify(data) }),
    blueprint: (data: any) => fetchJSON<any>("/api/v1/workflows/blueprint", { method: "POST", body: JSON.stringify(data) }),
    classify: (data: any) => fetchJSON<any>("/api/v1/workflows/classify", { method: "POST", body: JSON.stringify(data) }),
    categories: () => fetchJSON<any>("/api/v1/workflows/categories"),
  },
};
