"use client";
import { useEffect, useState } from "react";
import { api, UserRecord } from "@/lib/api";
import Link from "next/link";
import { ListSkeleton } from "@/components/ui";

type UsersPayload = { users?: UserRecord[] } | UserRecord[];
type UserSummary = UserRecord & { goals_count?: number };

export default function UsersPage() {
  const [users, setUsers] = useState<UserSummary[]>([]);
  const [showCreate, setShowCreate] = useState(false);
  const [form, setForm] = useState({ name: "" });
  const [load, setLoad] = useState(true);

  useEffect(() => { api.users.list().then((d) => { const l = d as UsersPayload; setUsers(Array.isArray(l) ? l : l.users ?? []); }).catch(() => {}).finally(() => setLoad(false)); }, []);

  function create() {
    if (!form.name.trim()) return;
    api.users.create({ username: form.name.trim() }).then(() => {
      setForm({ name: "" }); setShowCreate(false);
      api.users.list().then((d) => { const l = d as UsersPayload; setUsers(Array.isArray(l) ? l : l.users ?? []); }).catch(() => {});
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
          <input aria-label="Username" value={form.name} onChange={(e) => setForm(f => ({...f, name: e.target.value}))}
            placeholder="Username" className="w-full bg-surface border border-border rounded-lg px-3 py-2 text-sm" />
          <button type="button" onClick={create} disabled={!form.name.trim()}
            className="px-4 py-2 bg-accent text-black rounded-lg text-sm font-medium disabled:opacity-40">Create</button>
        </div>
      )}

      {load ? <ListSkeleton rows={3} /> : users.length === 0 ? (
        <p className="text-sm text-muted text-center py-8">No users registered. Create your first user above.</p>
      ) : (
        <div className="grid gap-3">
          {users.map((u) => (
            <Link key={u.id} href={`/users/${u.id}`} className="bg-card border border-border rounded-xl p-4 hover:border-accent/30 transition-colors block">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-9 h-9 rounded-lg bg-accent/10 flex items-center justify-center text-accent text-sm font-mono font-bold">
                    {(u.display_name || u.username || u.id || "?").charAt(0).toUpperCase()}
                  </div>
                  <div>
                    <div className="text-sm font-medium">{u.display_name || u.username || u.id}</div>
                    <div className="text-[10px] text-muted font-mono">{u.role || "user"}</div>
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
