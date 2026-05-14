import { notFound } from "next/navigation";
import Link from "next/link";

import { CaseCard } from "@/components/CaseCard";
import { ScoreBar } from "@/components/ScoreBar";
import { loadRun, listRunIds } from "@/lib/load";
import { fmtCost, fmtPercent, fmtRelativeDate, fmtScore } from "@/lib/format";
import { summarize } from "@/lib/types";

export const dynamic = "force-dynamic";

export default async function RunDetailPage({
  params,
}: {
  params: { id: string };
}) {
  let run;
  try {
    run = await loadRun(params.id);
  } catch (e) {
    if ((e as NodeJS.ErrnoException).code === "ENOENT") notFound();
    throw e;
  }
  const summary = summarize(run);
  const allIds = await listRunIds();
  const otherIds = allIds.filter((id) => id !== run.run_id);

  const failed = run.cases.filter((c) => !c.passed);
  const passed = run.cases.filter((c) => c.passed);

  return (
    <div className="space-y-6">
      <div>
        <Link
          href="/"
          className="text-xs text-ink-dim transition hover:text-ink-base"
        >
          ← all runs
        </Link>
        <div className="mt-2 flex items-end justify-between">
          <div>
            <h1 className="text-2xl font-semibold tracking-tight">
              {run.candidate_label}
            </h1>
            <p className="mt-1 font-mono text-xs text-ink-dim">{run.run_id}</p>
            <p className="mt-1 text-sm text-ink-muted">
              {fmtRelativeDate(run.started_at)} ·{" "}
              <span className="font-mono">{run.dataset_path}</span>
            </p>
          </div>
          {otherIds.length > 0 && (
            <Link
              href={`/compare?a=${otherIds[0]}&b=${run.run_id}`}
              className="rounded-lg border border-bg-border bg-bg-panel px-3 py-1.5 text-sm text-ink-base transition hover:bg-bg-card"
            >
              Compare vs {otherIds[0].slice(0, 8)}
            </Link>
          )}
        </div>
      </div>

      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        <Tile label="Pass rate" value={fmtPercent(summary.pass_rate)} tone={summary.pass_rate >= 0.8 ? "good" : summary.pass_rate >= 0.5 ? "neutral" : "bad"} />
        <Tile label="Mean score" value={fmtScore(summary.mean_score)} />
        <Tile label="Cases" value={String(summary.case_count)} />
        <Tile label="Total cost" value={fmtCost(summary.total_cost_usd)} />
      </div>

      <div className="card">
        <div className="mb-1 text-xs uppercase tracking-wide text-ink-dim">
          Mean score
        </div>
        <ScoreBar score={summary.mean_score} width="w-full" />
      </div>

      {failed.length > 0 && (
        <section className="space-y-3">
          <h2 className="text-sm font-semibold uppercase tracking-wide text-ink-muted">
            Failures ({failed.length})
          </h2>
          {failed.map((c) => (
            <CaseCard key={c.case_id} result={c} />
          ))}
        </section>
      )}

      {passed.length > 0 && (
        <section className="space-y-3">
          <h2 className="text-sm font-semibold uppercase tracking-wide text-ink-muted">
            Passed ({passed.length})
          </h2>
          {passed.map((c) => (
            <CaseCard key={c.case_id} result={c} />
          ))}
        </section>
      )}
    </div>
  );
}

function Tile({
  label,
  value,
  tone = "neutral",
}: {
  label: string;
  value: string;
  tone?: "good" | "bad" | "neutral";
}) {
  const toneClass =
    tone === "good"
      ? "text-accent-green"
      : tone === "bad"
      ? "text-accent-red"
      : "text-ink-base";
  return (
    <div className="card">
      <div className="text-xs uppercase tracking-wide text-ink-dim">{label}</div>
      <div className={`mt-1 font-mono text-2xl ${toneClass}`}>{value}</div>
    </div>
  );
}
