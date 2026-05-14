from __future__ import annotations

from typing import ClassVar

from evalkit.judges.base import Judge
from evalkit.types import TestCase, Verdict


class ExactMatchJudge(Judge):
    """Pass iff candidate_output (after optional normalization) equals
    case.expected['answer']."""

    kind: ClassVar[str] = "exact_match"

    def __init__(
        self,
        name: str,
        weight: float = 1.0,
        case_sensitive: bool = False,
        strip: bool = True,
    ):
        super().__init__(name=name, weight=weight)
        self.case_sensitive = case_sensitive
        self.strip = strip

    def _normalize(self, s: str) -> str:
        if self.strip:
            s = s.strip()
        if not self.case_sensitive:
            s = s.lower()
        return s

    async def evaluate(self, case: TestCase, candidate_output: str) -> Verdict:
        expected = case.expected.get("answer")
        if expected is None:
            return Verdict(
                judge_name=self.name,
                judge_kind=self.kind,
                passed=False,
                score=0.0,
                reasoning="expected.answer is missing in test case",
                failed_criteria=["expected.answer missing"],
            )
        passed = self._normalize(candidate_output) == self._normalize(str(expected))
        return Verdict(
            judge_name=self.name,
            judge_kind=self.kind,
            passed=passed,
            score=1.0 if passed else 0.0,
            reasoning=(
                "exact match" if passed else f"expected={expected!r} got={candidate_output!r}"
            ),
            failed_criteria=[] if passed else ["answer mismatch"],
        )
