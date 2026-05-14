import type { DiffResult, RunResult } from "./types";
import { summarize } from "./types";

export function diffRuns(
  baseline: RunResult,
  candidate: RunResult,
): DiffResult {
  const baseById = new Map(baseline.cases.map((c) => [c.case_id, c]));
  const candById = new Map(candidate.cases.map((c) => [c.case_id, c]));

  const regressed: DiffResult["regressed"] = [];
  const fixed: DiffResult["fixed"] = [];
  const score_deltas: Record<string, number> = {};
  let unchanged = 0;

  for (const [caseId, candCase] of candById) {
    const baseCase = baseById.get(caseId);
    if (!baseCase) continue;
    const delta = candCase.aggregate_score - baseCase.aggregate_score;
    score_deltas[caseId] = delta;
    if (baseCase.passed && !candCase.passed) {
      regressed.push({
        case_id: caseId,
        baseline_score: baseCase.aggregate_score,
        candidate_score: candCase.aggregate_score,
        failed_criteria: candCase.verdicts.flatMap((v) => v.failed_criteria),
      });
    } else if (!baseCase.passed && candCase.passed) {
      fixed.push({ case_id: caseId, delta });
    } else {
      unchanged++;
    }
  }

  const new_cases = [...candById.keys()].filter((id) => !baseById.has(id));
  const removed_cases = [...baseById.keys()].filter((id) => !candById.has(id));

  const baseSummary = summarize(baseline);
  const candSummary = summarize(candidate);

  return {
    baseline_run_id: baseline.run_id,
    candidate_run_id: candidate.run_id,
    baseline_label: baseline.candidate_label,
    candidate_label: candidate.candidate_label,
    pass_rate_delta: candSummary.pass_rate - baseSummary.pass_rate,
    mean_score_delta: candSummary.mean_score - baseSummary.mean_score,
    regressed,
    fixed,
    unchanged_count: unchanged,
    new_cases,
    removed_cases,
    score_deltas,
  };
}
