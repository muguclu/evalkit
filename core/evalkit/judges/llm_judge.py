from __future__ import annotations

import json
import os
import time
from typing import Any, ClassVar

from anthropic import AsyncAnthropic

from evalkit.judges.base import Judge
from evalkit.types import TestCase, Verdict

DEFAULT_RUBRIC = [
    {
        "name": "faithfulness",
        "description": "The answer is grounded in the provided context and contains no fabrications.",
        "weight": 1.0,
    },
    {
        "name": "relevance",
        "description": "The answer directly addresses the question asked.",
        "weight": 1.0,
    },
    {
        "name": "completeness",
        "description": "The answer covers all important aspects of the question.",
        "weight": 1.0,
    },
]

DEFAULT_SYSTEM = """You are a strict evaluator of LLM outputs. \
Given a question, optional context, an expected behavior, and a candidate answer, \
score the candidate against each rubric criterion on a 0.0-1.0 scale. \
Be calibrated: 1.0 means flawless, 0.5 means partially meets the criterion, 0.0 means total failure. \
Always cite the specific text from the candidate that supports your score."""

# USD per million tokens. Update as needed.
PRICING: dict[str, tuple[float, float]] = {
    "claude-opus-4-7": (15.0, 75.0),
    "claude-sonnet-4-6": (3.0, 15.0),
    "claude-sonnet-4-5": (3.0, 15.0),
    "claude-haiku-4-5": (1.0, 5.0),
}


def _estimate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    for prefix, (in_price, out_price) in PRICING.items():
        if model.startswith(prefix):
            return (input_tokens / 1_000_000) * in_price + (
                output_tokens / 1_000_000
            ) * out_price
    return 0.0


class LLMJudge(Judge):
    """LLM-as-judge with a structured Pydantic-validated rubric.

    Uses Claude tool-use to force the judge into emitting a typed verdict
    per rubric criterion, not just a free-form score.
    """

    kind: ClassVar[str] = "llm_judge"

    def __init__(
        self,
        name: str,
        weight: float = 1.0,
        model: str = "claude-sonnet-4-6",
        rubric: list[dict[str, Any]] | None = None,
        threshold: float = 0.7,
        system: str | None = None,
        max_tokens: int = 1024,
    ):
        super().__init__(name=name, weight=weight)
        self.model = model
        self.rubric = rubric or DEFAULT_RUBRIC
        self.threshold = threshold
        self.system = system or DEFAULT_SYSTEM
        self.max_tokens = max_tokens
        self._client = AsyncAnthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

    def _verdict_tool(self) -> dict[str, Any]:
        criteria_names = [c["name"] for c in self.rubric]
        return {
            "name": "emit_verdict",
            "description": "Return a structured verdict scoring the candidate answer.",
            "input_schema": {
                "type": "object",
                "required": ["scores", "overall_reasoning"],
                "properties": {
                    "scores": {
                        "type": "object",
                        "required": criteria_names,
                        "properties": {
                            name: {
                                "type": "object",
                                "required": ["score", "evidence", "passed"],
                                "properties": {
                                    "score": {"type": "number", "minimum": 0, "maximum": 1},
                                    "evidence": {
                                        "type": "string",
                                        "description": "Quote from the candidate that justifies the score.",
                                    },
                                    "passed": {"type": "boolean"},
                                },
                            }
                            for name in criteria_names
                        },
                    },
                    "overall_reasoning": {"type": "string"},
                },
            },
        }

    def _build_prompt(self, case: TestCase, candidate_output: str) -> str:
        question = case.input.get("question") or case.input.get("query") or json.dumps(
            case.input, ensure_ascii=False
        )
        rubric_text = "\n".join(
            f"- {c['name']} (weight {c.get('weight', 1.0)}): {c['description']}"
            for c in self.rubric
        )
        sections: list[str] = [f"<question>\n{question}\n</question>"]
        if case.context:
            sections.append(f"<context>\n{case.context}\n</context>")
        if case.expected:
            sections.append(
                f"<expected_behavior>\n{json.dumps(case.expected, ensure_ascii=False, indent=2)}\n</expected_behavior>"
            )
        sections.append(f"<candidate_answer>\n{candidate_output}\n</candidate_answer>")
        sections.append(f"<rubric>\n{rubric_text}\n</rubric>")
        sections.append(
            "Call emit_verdict exactly once with a score for every rubric criterion. "
            "Set passed=true iff the candidate clearly satisfies the criterion."
        )
        return "\n\n".join(sections)

    async def evaluate(self, case: TestCase, candidate_output: str) -> Verdict:
        prompt = self._build_prompt(case, candidate_output)
        tool = self._verdict_tool()

        t0 = time.perf_counter()
        try:
            response = await self._client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                system=self.system,
                tools=[tool],
                tool_choice={"type": "tool", "name": "emit_verdict"},
                messages=[{"role": "user", "content": prompt}],
            )
        except Exception as e:
            return Verdict(
                judge_name=self.name,
                judge_kind=self.kind,
                passed=False,
                score=0.0,
                reasoning=f"judge call failed: {type(e).__name__}: {e}",
                failed_criteria=["judge error"],
                latency_ms=(time.perf_counter() - t0) * 1000,
            )

        latency_ms = (time.perf_counter() - t0) * 1000
        tool_use_block = next(
            (b for b in response.content if getattr(b, "type", None) == "tool_use"),
            None,
        )
        if tool_use_block is None:
            return Verdict(
                judge_name=self.name,
                judge_kind=self.kind,
                passed=False,
                score=0.0,
                reasoning="judge did not emit a tool_use block",
                failed_criteria=["no tool_use"],
                latency_ms=latency_ms,
            )

        payload: dict[str, Any] = tool_use_block.input  # type: ignore[assignment]
        scores: dict[str, dict[str, Any]] = payload.get("scores", {})

        total_weight = sum(c.get("weight", 1.0) for c in self.rubric)
        weighted = 0.0
        failed_criteria: list[str] = []
        for crit in self.rubric:
            name = crit["name"]
            w = crit.get("weight", 1.0)
            entry = scores.get(name, {})
            s = float(entry.get("score", 0.0))
            weighted += s * w
            if not entry.get("passed", False):
                evidence = entry.get("evidence", "")
                failed_criteria.append(f"{name} (score={s:.2f}): {evidence}")
        aggregate = weighted / total_weight if total_weight else 0.0
        passed = aggregate >= self.threshold and not failed_criteria

        usage = response.usage
        cost = _estimate_cost(self.model, usage.input_tokens, usage.output_tokens)

        return Verdict(
            judge_name=self.name,
            judge_kind=self.kind,
            passed=passed,
            score=aggregate,
            reasoning=payload.get("overall_reasoning", ""),
            failed_criteria=failed_criteria,
            cost_usd=cost,
            latency_ms=latency_ms,
            raw={
                "scores": scores,
                "model": self.model,
                "input_tokens": usage.input_tokens,
                "output_tokens": usage.output_tokens,
            },
        )
