// Mirrors the Pydantic schema in core/evalkit/types.py.
// Keep field names in sync — the API routes pass these through verbatim.

export interface JudgeConfig {
  kind: "exact_match" | "contains" | "llm_judge" | "composite";
  name?: string | null;
  weight: number;
  config: Record<string, unknown>;
}

export interface Verdict {
  judge_name: string;
  judge_kind: string;
  passed: boolean;
  score: number;
  reasoning: string;
  failed_criteria: string[];
  cost_usd: number;
  latency_ms: number;
  raw: {
    scores?: Record<
      string,
      { score: number; evidence: string; passed: boolean }
    >;
    model?: string;
    input_tokens?: number;
    output_tokens?: number;
    children?: Verdict[];
  };
}

export interface CaseResult {
  case_id: string;
  candidate_output: string;
  verdicts: Verdict[];
  aggregate_score: number;
  passed: boolean;
  tags: string[];
  error: string | null;
}

export interface RunResult {
  run_id: string;
  started_at: string;
  finished_at: string;
  dataset_path: string;
  candidate_label: string;
  cases: CaseResult[];
}

export interface RunSummary {
  run_id: string;
  candidate_label: string;
  started_at: string;
  finished_at: string;
  case_count: number;
  pass_rate: number;
  mean_score: number;
  total_cost_usd: number;
}

export interface DiffResult {
  baseline_run_id: string;
  candidate_run_id: string;
  baseline_label: string;
  candidate_label: string;
  pass_rate_delta: number;
  mean_score_delta: number;
  regressed: Array<{
    case_id: string;
    baseline_score: number;
    candidate_score: number;
    failed_criteria: string[];
  }>;
  fixed: Array<{ case_id: string; delta: number }>;
  unchanged_count: number;
  new_cases: string[];
  removed_cases: string[];
  score_deltas: Record<string, number>;
}

export function summarize(run: RunResult): RunSummary {
  const passed = run.cases.filter((c) => c.passed).length;
  const meanScore = run.cases.length
    ? run.cases.reduce((a, c) => a + c.aggregate_score, 0) / run.cases.length
    : 0;
  const cost = run.cases.reduce(
    (a, c) => a + c.verdicts.reduce((b, v) => b + v.cost_usd, 0),
    0,
  );
  return {
    run_id: run.run_id,
    candidate_label: run.candidate_label,
    started_at: run.started_at,
    finished_at: run.finished_at,
    case_count: run.cases.length,
    pass_rate: run.cases.length ? passed / run.cases.length : 0,
    mean_score: meanScore,
    total_cost_usd: cost,
  };
}
