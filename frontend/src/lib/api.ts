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
};
