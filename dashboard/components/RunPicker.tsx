"use client";

import { useRouter, useSearchParams } from "next/navigation";

import type { RunSummary } from "@/lib/types";

export function RunPicker({
  runs,
  param,
  label,
}: {
  runs: RunSummary[];
  param: "a" | "b";
  label: string;
}) {
  const router = useRouter();
  const search = useSearchParams();
  const current = search.get(param) ?? "";

  return (
    <label className="flex flex-col gap-1.5">
      <span className="text-xs uppercase tracking-wide text-ink-dim">
        {label}
      </span>
      <select
        value={current}
        onChange={(e) => {
          const params = new URLSearchParams(search.toString());
          if (e.target.value) params.set(param, e.target.value);
          else params.delete(param);
          router.replace(`/compare?${params.toString()}`);
        }}
        className="rounded-lg border border-bg-border bg-bg-panel px-3 py-2 font-mono text-sm text-ink-base outline-none focus:border-accent-violet/40"
      >
        <option value="">— select run —</option>
        {runs.map((r) => (
          <option key={r.run_id} value={r.run_id}>
            {r.candidate_label} · {r.run_id.slice(0, 8)}
          </option>
        ))}
      </select>
    </label>
  );
}
