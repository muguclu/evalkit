from __future__ import annotations

import asyncio
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Awaitable, Callable

from evalkit.judges import build_judge
from evalkit.types import CaseResult, RunResult, TestCase, Verdict

CandidateFn = Callable[[TestCase], Awaitable[str]]


class Runner:
    """Orchestrates eval runs over a list of TestCases.

    The caller supplies a `candidate_fn` — an async function that takes a
    TestCase and returns the candidate system's output string. The runner
    fans cases out concurrently (bounded by `concurrency`) and applies each
    case's judges to score them.
    """

    def __init__(
        self,
        candidate_fn: CandidateFn,
        candidate_label: str,
        concurrency: int = 4,
        on_case_complete: Callable[[CaseResult], None] | None = None,
    ):
        self.candidate_fn = candidate_fn
        self.candidate_label = candidate_label
        self.concurrency = concurrency
        self.on_case_complete = on_case_complete

    async def _evaluate_case(self, case: TestCase) -> CaseResult:
        try:
            output = await self.candidate_fn(case)
        except Exception as e:
            return CaseResult(
                case_id=case.id,
                candidate_output="",
                verdicts=[],
                aggregate_score=0.0,
                passed=False,
                tags=case.tags,
                error=f"candidate_fn failed: {type(e).__name__}: {e}",
            )

        if not case.judges:
            return CaseResult(
                case_id=case.id,
                candidate_output=output,
                verdicts=[],
                aggregate_score=0.0,
                passed=False,
                tags=case.tags,
                error="no judges configured for this case",
            )

        verdicts: list[Verdict] = []
        for judge_cfg in case.judges:
            judge = build_judge(judge_cfg)
            verdicts.append(await judge.evaluate(case, output))

        total_weight = sum(v_cfg.weight for v_cfg in case.judges) or 1.0
        aggregate = (
            sum(v.score * cfg.weight for v, cfg in zip(verdicts, case.judges))
            / total_weight
        )
        passed = all(v.passed for v in verdicts)

        return CaseResult(
            case_id=case.id,
            candidate_output=output,
            verdicts=verdicts,
            aggregate_score=aggregate,
            passed=passed,
            tags=case.tags,
        )

    async def run(self, cases: list[TestCase], dataset_path: str | Path) -> RunResult:
        sem = asyncio.Semaphore(self.concurrency)

        async def bounded(case: TestCase) -> CaseResult:
            async with sem:
                result = await self._evaluate_case(case)
                if self.on_case_complete:
                    self.on_case_complete(result)
                return result

        started = datetime.now(timezone.utc)
        case_results = await asyncio.gather(*(bounded(c) for c in cases))
        finished = datetime.now(timezone.utc)

        return RunResult(
            run_id=uuid.uuid4().hex[:12],
            started_at=started,
            finished_at=finished,
            dataset_path=str(dataset_path),
            candidate_label=self.candidate_label,
            cases=case_results,
        )
