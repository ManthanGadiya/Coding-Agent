"use client";
import { useEffect, useState } from "react";
import { onApiError } from "@/lib/api";

export function ApiErrorBanner() {
  const [message, setMessage] = useState<string | null>(null);

  useEffect(() => onApiError(setMessage), []);

  if (!message) return null;
  return (
    <div className="fixed bottom-4 right-4 z-50 max-w-md bg-card border border-red-500/40 rounded-xl p-4 shadow-xl">
      <div className="flex items-start gap-3">
        <div className="flex-1 min-w-0">
          <p className="text-sm font-semibold text-red-400">API request failed</p>
          <p className="text-xs text-muted mt-1 break-words">{message}</p>
        </div>
        <button type="button" onClick={() => setMessage(null)}
          className="text-muted hover:text-red-400 text-sm leading-none px-1"
          aria-label="Dismiss error">✕</button>
      </div>
    </div>
  );
}
