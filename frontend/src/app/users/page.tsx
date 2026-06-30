"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import Link from "next/link";
import { ListSkeleton } from "@/components/ui";

export default function UsersPage() {
  const [users, setUsers] = useState<any[]>([]);
  const [showCreate, setShowCreate] = useState(false);
  const [form, setForm] = useState({ name: "", role: "developer" });
  const [load, setLoad] = useState(true);

  useEffect(() => { api.users.list().then((d: any) => setUsers(Array.isArray(d) ? d : [])).catch(() => {}).finally(() => setLoad(false)); }, []);

  function create() {
    if (!form.name.trim()) return;
    api.users.create({ name: form.name.trim(), role: form.role }).then(() => {
      setForm({ name: "", role: "developer" }); setShowCreate(false);
      api.users.list().then(setUsers).catch(() => {});
    }).catch(() => {});
  }

  return (
    <div className="space-y-8">
      <div className="animate-in flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Users</h1>
          <p className="text-muted text-sm mt-1">{users.length} registered users</p>
        </div>
        <button type="button" onClick={() => setShowCreate(!showCreate)}
          className="px-4 py-2 bg-accent text-black rounded-lg text-sm font-medium">{showCreate ? "Cancel" : "+ Add User"}</button>
      </div>

      {showCreate && (
        <div className="bg-card border border-border rounded-xl p-5 space-y-3 animate-in">
          <input value={form.name} onChange={(e) => setForm(f => ({...f, name: e.target.value}))}
            placeholder="Name" className="w-full bg-surface border border-border rounded-lg px-3 py-2 text-sm" />
          <select value={form.role} onChange={(e) => setForm(f => ({...f, role: e.target.value}))}
            className="bg-surface border border-border rounded-lg px-3 py-2 text-sm">
            {["developer", "admin", "manager", "viewer"].map(r => <option key={r} value={r}>{r}</option>)}
          </select>
          <button type="button" onClick={create} disabled={!form.name.trim()}
            className="px-4 py-2 bg-accent text-black rounded-lg text-sm font-medium disabled:opacity-40">Create</button>
        </div>
      )}

      {load ? <ListSkeleton rows={3} /> : users.length === 0 ? (
        <p className="text-sm text-muted text-center py-8">No users registered. Create your first user above.</p>
      ) : (
        <div className="grid gap-3">
          {users.map((u: any) => (
            <Link key={u.id} href={`/users/${u.id}`} className="bg-card border border-border rounded-xl p-4 hover:border-accent/30 transition-colors block">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-9 h-9 rounded-lg bg-accent/10 flex items-center justify-center text-accent text-sm font-mono font-bold">
                    {(u.name || u.id || "?").charAt(0).toUpperCase()}
                  </div>
                  <div>
                    <div className="text-sm font-medium">{u.name || u.id}</div>
                    <div className="text-[10px] text-muted font-mono">{u.role || "developer"}</div>
                  </div>
                </div>
                <span className="text-xs text-muted font-mono">{u.goals_count ?? 0} goals</span>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
