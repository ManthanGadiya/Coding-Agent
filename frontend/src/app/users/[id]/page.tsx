"use client";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { api } from "@/lib/api";
import Link from "next/link";
import { Skeleton, CardSkeleton, ListSkeleton } from "@/components/ui";

export default function UserDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [user, setUser] = useState<any>(null);
  const [goals, setGoals] = useState<any[]>([]);
  const [goalForm, setGoalForm] = useState<{ show: boolean; goal: string }>({ show: false, goal: "" });

  useEffect(() => {
    if (!id) return;
    api.users.get(id).then(setUser).catch(() => {});
    api.users.goals(id).then((d: any) => setGoals(Array.isArray(d) ? d : d.goals ?? [])).catch(() => {});
  }, [id]);

  function createGoal() {
    if (!goalForm.goal.trim()) return;
    api.users.createGoal(id, { title: goalForm.goal.trim() }).then(() => {
      setGoalForm({ show: false, goal: "" });
      api.users.goals(id).then((d: any) => setGoals(Array.isArray(d) ? d : d.goals ?? [])).catch(() => {});
    }).catch(() => {});
  }

  function toggleGoal(userId: string, goalId: string, completed: boolean) {
    api.users.updateGoal(userId, goalId, { status: completed ? "completed" : "active" }).then(() => {
      api.users.goals(userId).then((d: any) => setGoals(Array.isArray(d) ? d : d.goals ?? [])).catch(() => {});
    }).catch(() => {});
  }

  if (!user) return (
    <div className="space-y-6 animate-in">
      <Skeleton className="h-4 w-20" />
      <div className="flex items-center gap-4">
        <Skeleton className="w-12 h-12 rounded-xl" />
        <div className="space-y-2">
          <Skeleton className="h-7 w-40" />
          <Skeleton className="h-4 w-24" />
        </div>
      </div>
      <div className="grid grid-cols-4 gap-3">
        {Array.from({length: 4}).map((_, i) => <CardSkeleton key={i} />)}
      </div>
      <ListSkeleton rows={3} />
    </div>
  );

  return (
    <div className="space-y-8">
      <div className="animate-in">
        <Link href="/users" className="text-xs text-muted hover:text-foreground">← Back to Users</Link>
        <div className="flex items-center gap-4 mt-3">
          <div className="w-12 h-12 rounded-xl bg-accent/10 flex items-center justify-center text-accent text-xl font-mono font-bold">
            {(user.display_name || user.username || user.id || "?").charAt(0).toUpperCase()}
          </div>
          <div>
            <h1 className="text-2xl font-bold tracking-tight">{user.display_name || user.username || user.id}</h1>
            <p className="text-muted text-sm font-mono">{user.role || "user"}</p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-4 gap-3">
        {[
          { label: "Projects", value: user.project_count ?? 0 },
          { label: "Goals", value: goals.length },
          { label: "Active Goals", value: goals.filter((g: any) => g.status !== "completed").length },
          {label: "Role", value: user.role || "user" },
        ].map((s) => (
          <div key={s.label} className="bg-card border border-border rounded-xl p-4">
            <div className="text-[10px] text-muted">{s.label}</div>
            <div className="text-xl font-mono font-bold text-accent mt-1">{s.value}</div>
          </div>
        ))}
      </div>

      <div className="bg-card border border-border rounded-xl p-5">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-sm font-semibold">Goals ({goals.length})</h2>
          <button type="button" onClick={() => setGoalForm(f => ({...f, show: !f.show}))}
            className="px-3 py-1.5 bg-accent/10 text-accent rounded-lg text-xs font-medium">
            {goalForm.show ? "Cancel" : "+ Add Goal"}
          </button>
        </div>

        {goalForm.show && (
          <div className="flex gap-2 mb-4">
            <input aria-label="Goal description" value={goalForm.goal} onChange={(e) => setGoalForm(f => ({...f, goal: e.target.value}))}
              placeholder="Goal description" className="flex-1 bg-surface border border-border rounded-lg px-3 py-2 text-sm" />
            <button type="button" onClick={createGoal} disabled={!goalForm.goal.trim()}
              className="px-3 py-2 bg-accent text-black rounded-lg text-sm font-medium disabled:opacity-40">Add</button>
          </div>
        )}

        {goals.length === 0 ? (
          <p className="text-sm text-muted text-center py-6">No goals yet. Add a goal above to track this user's objectives.</p>
        ) : (
          <div className="space-y-2">
            {goals.map((g: any) => (
              <div key={g.id} className="flex items-center gap-3 bg-surface rounded-lg px-4 py-3">
                <input aria-label="Mark goal complete" type="checkbox" checked={g.status === "completed"} onChange={() => toggleGoal(id, g.id, g.status !== "completed")}
                  className="rounded accent-accent" />
                <span className={`text-sm flex-1 ${g.status === "completed" ? "line-through text-muted" : ""}`}>{g.title}</span>
                <span className="px-2 py-0.5 rounded text-xs font-mono bg-surface text-muted">{g.domain}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
