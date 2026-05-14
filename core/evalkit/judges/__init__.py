from evalkit.judges.base import Judge
from evalkit.judges.exact_match import ExactMatchJudge
from evalkit.judges.contains import ContainsJudge
from evalkit.judges.llm_judge import LLMJudge
from evalkit.judges.composite import CompositeJudge
from evalkit.types import JudgeConfig

JUDGE_REGISTRY: dict[str, type[Judge]] = {
    "exact_match": ExactMatchJudge,
    "contains": ContainsJudge,
    "llm_judge": LLMJudge,
    "composite": CompositeJudge,
}


def build_judge(config: JudgeConfig) -> Judge:
    """Instantiate a judge from a JudgeConfig."""
    cls = JUDGE_REGISTRY.get(config.kind)
    if cls is None:
        raise ValueError(f"Unknown judge kind: {config.kind}")
    return cls.from_config(config)


__all__ = [
    "Judge",
    "ExactMatchJudge",
    "ContainsJudge",
    "LLMJudge",
    "CompositeJudge",
    "JUDGE_REGISTRY",
    "build_judge",
]
