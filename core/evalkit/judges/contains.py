from __future__ import annotations

from typing import ClassVar

from evalkit.judges.base import Judge
from evalkit.types import TestCase, Verdict


class ContainsJudge(Judge):
    """Checks that the candidate output contains all required phrases and none of
    the forbidden phrases.

    Reads from case.expected:
      must_mention: list[str]
      must_not_mention: list[str]
    """

    kind: ClassVar[str] = "contains"

    def __init__(self, name: str, weight: float = 1.0, case_sensitive: bool = False):
        super().__init__(name=name, weight=weight)
        self.case_sensitive = case_sensitive

    def _contains(self, haystack: str, needle: str) -> bool:
        if self.case_sensitive:
            return needle in haystack
        return needle.lower() in haystack.lower()

    async def evaluate(self, case: TestCase, candidate_output: str) -> Verdict:
        must = case.expected.get("must_mention", []) or []
        must_not = case.expected.get("must_not_mention", []) or []

        missing = [p for p in must if not self._contains(candidate_output, p)]
        leaked = [p for p in must_not if self._contains(candidate_output, p)]

        total_checks = max(len(must) + len(must_not), 1)
        failures = len(missing) + len(leaked)
        score = max(0.0, 1.0 - failures / total_checks)
        passed = failures == 0

        failed_criteria: list[str] = []
        if missing:
            failed_criteria.append(f"missing required phrases: {missing}")
        if leaked:
            failed_criteria.append(f"forbidden phrases present: {leaked}")

        return Verdict(
            judge_name=self.name,
            judge_kind=self.kind,
            passed=passed,
            score=score,
            reasoning=(
                "all phrase checks passed"
                if passed
                else f"{failures}/{total_checks} phrase checks failed"
            ),
            failed_criteria=failed_criteria,
        )
