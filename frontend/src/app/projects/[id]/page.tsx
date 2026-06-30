"use client";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { api } from "@/lib/api";
import Link from "next/link";

export default function ProjectDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [project, setProject] = useState<any>(null);
  const [stats, setStats] = useState<any>(null);
  const [tasks, setTasks] = useState<any[]>([]);

  useEffect(() => {
    if (!id) return;
    api.projects.get(id).then(setProject).catch(() => {});
    api.projects.stats(id).then(setStats).catch(() => {});
    api.tasks.list(`project_id=${id}`).then(setTasks).catch(() => {});
  }, [id]);

  if (!project) return <div className="text-sm text-muted animate-in">Loading...</div>;

  return (
    <div className="space-y-8">
      <div className="animate-in">
        <Link href="/projects" className="text-xs text-muted hover:text-foreground mb-2 inline-block">&larr; Projects</Link>
        <h1 className="text-2xl font-bold tracking-tight">{project.name}</h1>
        <p className="text-muted text-sm mt-1">{project.description || "No description"}</p>
      </div>

      {stats && (
        <div className="grid grid-cols-4 gap-3 animate-in">
          <StatCard label="Tasks" value={stats.total_tasks ?? tasks.length} />
          <StatCard label="Completed" value={stats.completed_tasks ?? tasks.filter((t) => t.status === "completed").length} />
          <StatCard label="Completion" value={stats.completion_rate != null ? `${Math.round(stats.completion_rate * 100)}%` : "—"} />
          <StatCard label="Arch Decisions" value={stats.architecture_decisions ?? "—"} />
        </div>
      )}

      {project.tech_stack && (
        <div className="bg-card border border-border rounded-xl p-5 animate-in">
          <h2 className="text-sm font-semibold mb-2">Tech Stack</h2>
          <div className="flex flex-wrap gap-2">
            {(Array.isArray(project.tech_stack) ? project.tech_stack : []).map((t: string) => (
              <span key={t} className="px-2 py-1 bg-surface rounded text-xs font-mono">{t}</span>
            ))}
          </div>
        </div>
      )}

      <div className="bg-card border border-border rounded-xl p-5 animate-in">
        <h2 className="text-sm font-semibold mb-3">Tasks ({tasks.length})</h2>
        <div className="space-y-2">
          {tasks.map((t: any) => (
            <div key={t.id} className="flex items-center gap-3 bg-surface rounded-lg px-3 py-2">
              <span className={`w-2 h-2 rounded-full ${t.status === "completed" ? "bg-success" : t.status === "in_progress" ? "bg-accent" : t.status === "failed" ? "bg-red-500" : "bg-yellow-500"}`} />
              <span className="text-xs font-mono flex-1">{t.title}</span>
              <span className="text-[10px] text-muted">{t.task_type}</span>
              {t.assigned_agent && <span className="text-[10px] font-mono text-muted">{t.assigned_agent}</span>}
            </div>
          ))}
          {tasks.length === 0 && <p className="text-xs text-muted">No tasks for this project.</p>}
        </div>
      </div>
    </div>
  );
}

function StatCard({ label, value }: { label: string; value: any }) {
  return (
    <div className="bg-card border border-border rounded-xl p-4">
      <div className="text-[10px] text-muted">{label}</div>
      <div className="text-xl font-bold font-mono mt-1">{value ?? "—"}</div>
    </div>
  );
}
