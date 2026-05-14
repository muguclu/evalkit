import Link from "next/link";
import { Suspense } from "react";

import { RunPicker } from "@/components/RunPicker";
import { ScoreBar } from "@/components/ScoreBar";
import { diffRuns } from "@/lib/diff";
import { loadAllRuns, loadRun } from "@/lib/load";
import { fmtPercent, fmtScore } from "@/lib/format";
import { summarize } from "@/lib/types";

export const dynamic = "force-dynamic";

export default async function ComparePage({
  searchParams,
}: {
  searchParams: { a?: string; b?: string };
}) {
  const runs = (await loadAllRuns()).map(summarize);
  const a = searchParams.a;
  const b = searchParams.b;

  let body: React.ReactNode = (
    <div className="card text-center text-ink-muted">
      Pick a baseline and candidate run above.
    </div>
  );

  if (a && b) {
    if (a === b) {
      body = (
        <div className="card text-center text-ink-muted">
          Choose two different runs to compare.
        </div>
      );
    } else {
      try {
        const [baseRun, candRun] = await Promise.all([loadRun(a), loadRun(b)]);
        const diff = diffRuns(baseRun, candRun);
        body = <DiffView diff={diff} />;
      } catch {
        body = (
          <div className="card text-center text-accent-red">
            Failed to load one of the runs.
          </div>
        );
      }
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Compare runs</h1>
        <p className="mt-1 text-sm text-ink-muted">
          Diff two runs to spot regressions and fixed cases.
        </p>
      </div>

      <Suspense fallback={null}>
        <div className="card grid grid-cols-1 gap-4 sm:grid-cols-2">
          <RunPicker runs={runs} param="a" label="Baseline" />
          <RunPicker runs={runs} param="b" label="Candidate" />
        </div>
      </Suspense>

      {body}
    </div>
  );
}

function DiffView({ diff }: { diff: ReturnType<typeof diffRuns> }) {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        <DeltaTile
          label="Pass rate Δ"
          value={fmtPercent(diff.pass_rate_delta, 1)}
          delta={diff.pass_rate_delta}
        />
        <DeltaTile
          label="Mean score Δ"
          value={fmtScore(diff.mean_score_delta, 3)}
          delta={diff.mean_score_delta}
        />
        <SimpleTile label="Regressed" value={String(diff.regressed.length)} tone={diff.regressed.length > 0 ? "bad" : "neutral"} />
        <SimpleTile label="Fixed" value={String(diff.fixed.length)} tone={diff.fixed.length > 0 ? "good" : "neutral"} />
      </div>

      <div className="card">
        <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-ink-muted">
          Direction
        </h2>
        <div className="flex items-center justify-between gap-4 text-sm">
          <RunLink id={diff.baseline_run_id} label={diff.baseline_label} />
          <span className="text-ink-dim">→</span>
          <RunLink id={diff.candidate_run_id} label={diff.candidate_label} />
        </div>
      </div>

      {diff.regressed.length > 0 && (
        <section>
          <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-accent-red">
            Regressions ({diff.regressed.length})
          </h2>
          <div className="space-y-2">
            {diff.regressed.map((r) => (
              <div key={r.case_id} className="card border-accent-red/30 bg-accent-red/[0.03]">
                <div className="flex items-center justify-between">
                  <span className="font-mono text-sm text-ink-base">
                    {r.case_id}
                  </span>
                  <span className="font-mono text-xs text-ink-muted">
                    {r.baseline_score.toFixed(2)} → {r.candidate_score.toFixed(2)}
                  </span>
                </div>
                {r.failed_criteria.length > 0 && (
                  <ul className="mt-2 space-y-1 text-xs text-ink-muted">
                    {r.failed_criteria.slice(0, 5).map((f, i) => (
                      <li key={i}>· {f}</li>
                    ))}
                  </ul>
                )}
              </div>
            ))}
          </div>
        </section>
      )}

      {diff.fixed.length > 0 && (
        <section>
          <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-accent-green">
            Fixed ({diff.fixed.length})
          </h2>
          <div className="space-y-2">
            {diff.fixed.map((f) => (
              <div key={f.case_id} className="card border-accent-green/30 bg-accent-green/[0.03] flex items-center justify-between">
                <span className="font-mono text-sm text-ink-base">{f.case_id}</span>
                <span className="font-mono text-xs text-accent-green">+{f.delta.toFixed(2)}</span>
              </div>
            ))}
          </div>
        </section>
      )}

      {Object.keys(diff.score_deltas).length > 0 && (
        <section className="card">
          <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-ink-muted">
            Per-case score deltas
          </h2>
          <div className="space-y-2">
            {Object.entries(diff.score_deltas)
              .sort(([, a], [, b]) => a - b)
              .map(([caseId, delta]) => (
                <div key={caseId} className="flex items-center justify-between text-sm">
                  <span className="font-mono text-ink-base">{caseId}</span>
                  <div className="flex items-center gap-3">
                    <ScoreBar
                      score={Math.abs(delta)}
                      passed={delta >= 0}
                      width="w-32"
                    />
                    <span
                      className={`font-mono text-xs ${
                        delta > 0.005
                          ? "text-accent-green"
                          : delta < -0.005
                          ? "text-accent-red"
                          : "text-ink-dim"
                      }`}
                    >
                      {delta > 0 ? "+" : ""}
                      {delta.toFixed(3)}
                    </span>
                  </div>
                </div>
              ))}
          </div>
        </section>
      )}
    </div>
  );
}

function DeltaTile({ label, value, delta }: { label: string; value: string; delta: number }) {
  const tone = delta > 0.005 ? "good" : delta < -0.005 ? "bad" : "neutral";
  const sign = delta > 0 ? "+" : "";
  return (
    <SimpleTile label={label} value={`${sign}${value}`} tone={tone} />
  );
}

function SimpleTile({
  label,
  value,
  tone,
}: {
  label: string;
  value: string;
  tone: "good" | "bad" | "neutral";
}) {
  const toneClass =
    tone === "good" ? "text-accent-green" : tone === "bad" ? "text-accent-red" : "text-ink-base";
  return (
    <div className="card">
      <div className="text-xs uppercase tracking-wide text-ink-dim">{label}</div>
      <div className={`mt-1 font-mono text-2xl ${toneClass}`}>{value}</div>
    </div>
  );
}

function RunLink({ id, label }: { id: string; label: string }) {
  return (
    <Link href={`/runs/${id}`} className="flex-1 group">
      <div className="font-medium text-ink-base group-hover:text-accent-violet">{label}</div>
      <div className="font-mono text-xs text-ink-dim">{id.slice(0, 12)}</div>
    </Link>
  );
}
