import Link from "next/link";

import { ScoreBar } from "@/components/ScoreBar";
import { loadAllRuns } from "@/lib/load";
import { fmtCost, fmtPercent, fmtRelativeDate, fmtScore } from "@/lib/format";
import { summarize } from "@/lib/types";

export const dynamic = "force-dynamic";

export default async function HomePage() {
  const runs = (await loadAllRuns()).map(summarize);

  return (
    <div className="space-y-6">
      <div className="flex items-end justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Runs</h1>
          <p className="mt-1 text-sm text-ink-muted">
            {runs.length} {runs.length === 1 ? "run" : "runs"} on disk, newest first.
          </p>
        </div>
        {runs.length >= 2 && (
          <Link
            href={`/compare?a=${runs[runs.length - 1].run_id}&b=${runs[0].run_id}`}
            className="rounded-lg border border-bg-border bg-bg-panel px-3 py-1.5 text-sm text-ink-base transition hover:bg-bg-card"
          >
            Compare oldest → newest
          </Link>
        )}
      </div>

      {runs.length === 0 ? (
        <div className="card text-center">
          <p className="text-ink-muted">No runs found in <code className="font-mono">runs/</code>.</p>
          <p className="mt-2 text-xs text-ink-dim">
            Run an eval first:{" "}
            <code className="font-mono">python examples/turkish-legal-rag/run_eval.py</code>
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {runs.map((run) => (
            <Link
              key={run.run_id}
              href={`/runs/${run.run_id}`}
              className="card flex items-center justify-between transition hover:border-accent-violet/40 hover:bg-bg-card/80"
            >
              <div className="flex flex-1 items-center gap-5">
                <div className="font-mono text-xs text-ink-dim">
                  {run.run_id.slice(0, 8)}
                </div>
                <div className="flex-1">
                  <div className="font-medium text-ink-base">
                    {run.candidate_label}
                  </div>
                  <div className="mt-0.5 text-xs text-ink-dim">
                    {fmtRelativeDate(run.started_at)} · {run.case_count} cases
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-6">
                <Stat label="pass" value={fmtPercent(run.pass_rate)} />
                <Stat label="score" value={fmtScore(run.mean_score)} />
                <Stat label="cost" value={fmtCost(run.total_cost_usd)} />
                <div className="hidden sm:block">
                  <ScoreBar score={run.mean_score} width="w-24" />
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="text-right">
      <div className="font-mono text-sm text-ink-base">{value}</div>
      <div className="text-[10px] uppercase tracking-wide text-ink-dim">
        {label}
      </div>
    </div>
  );
}
