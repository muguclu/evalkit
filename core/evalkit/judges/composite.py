from __future__ import annotations

from typing import Any, ClassVar

from evalkit.judges.base import Judge
from evalkit.types import JudgeConfig, TestCase, Verdict


class CompositeJudge(Judge):
    """Weighted combination of multiple inner judges.

    Inner judges are configured via the `children` key in config, each of which
    is itself a JudgeConfig dict.
    """

    kind: ClassVar[str] = "composite"

    def __init__(
        self,
        name: str,
        weight: float = 1.0,
        children: list[dict[str, Any]] | None = None,
        threshold: float = 0.7,
    ):
        super().__init__(name=name, weight=weight)
        from evalkit.judges import build_judge

        self._children: list[Judge] = []
        for child_cfg in children or []:
            self._children.append(build_judge(JudgeConfig.model_validate(child_cfg)))
        self.threshold = threshold

    async def evaluate(self, case: TestCase, candidate_output: str) -> Verdict:
        if not self._children:
            return Verdict(
                judge_name=self.name,
                judge_kind=self.kind,
                passed=False,
                score=0.0,
                reasoning="composite judge has no children configured",
                failed_criteria=["no children"],
            )

        child_verdicts: list[Verdict] = []
        for child in self._children:
            child_verdicts.append(await child.evaluate(case, candidate_output))

        total_weight = sum(c.weight for c in self._children) or 1.0
        score = sum(v.score * c.weight for v, c in zip(child_verdicts, self._children)) / total_weight
        cost = sum(v.cost_usd for v in child_verdicts)
        latency = sum(v.latency_ms for v in child_verdicts)
        failed = [f for v in child_verdicts for f in v.failed_criteria]
        passed = score >= self.threshold and all(v.passed for v in child_verdicts)

        return Verdict(
            judge_name=self.name,
            judge_kind=self.kind,
            passed=passed,
            score=score,
            reasoning="; ".join(
                f"{v.judge_name}={v.score:.2f}{'[pass]' if v.passed else '[fail]'}"
                for v in child_verdicts
            ),
            failed_criteria=failed,
            cost_usd=cost,
            latency_ms=latency,
            raw={"children": [v.model_dump() for v in child_verdicts]},
        )
