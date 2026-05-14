from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class JudgeConfig(BaseModel):
    """Configuration for a single judge applied to a test case."""

    kind: Literal["exact_match", "contains", "llm_judge", "composite"]
    name: str | None = None
    weight: float = 1.0
    config: dict[str, Any] = Field(default_factory=dict)


class TestCase(BaseModel):
    """A single eval test case loaded from YAML."""

    id: str
    input: dict[str, Any]
    context: str | None = None
    expected: dict[str, Any] = Field(default_factory=dict)
    judges: list[JudgeConfig] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class Verdict(BaseModel):
    """Result of running one judge against one case."""

    judge_name: str
    judge_kind: str
    passed: bool
    score: float = Field(ge=0.0, le=1.0)
    reasoning: str = ""
    failed_criteria: list[str] = Field(default_factory=list)
    cost_usd: float = 0.0
    latency_ms: float = 0.0
    raw: dict[str, Any] = Field(default_factory=dict)


class CaseResult(BaseModel):
    """All verdicts for a single test case + the candidate output evaluated."""

    case_id: str
    candidate_output: str
    verdicts: list[Verdict]
    aggregate_score: float = Field(ge=0.0, le=1.0)
    passed: bool
    tags: list[str] = Field(default_factory=list)
    error: str | None = None


class RunResult(BaseModel):
    """Full eval run."""

    run_id: str
    started_at: datetime
    finished_at: datetime
    dataset_path: str
    candidate_label: str
    cases: list[CaseResult]

    @property
    def pass_rate(self) -> float:
        if not self.cases:
            return 0.0
        return sum(1 for c in self.cases if c.passed) / len(self.cases)

    @property
    def mean_score(self) -> float:
        if not self.cases:
            return 0.0
        return sum(c.aggregate_score for c in self.cases) / len(self.cases)

    @property
    def total_cost_usd(self) -> float:
        return sum(v.cost_usd for c in self.cases for v in c.verdicts)
