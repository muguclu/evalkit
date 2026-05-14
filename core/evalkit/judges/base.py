from __future__ import annotations

from abc import ABC, abstractmethod
from typing import ClassVar

from evalkit.types import JudgeConfig, TestCase, Verdict


class Judge(ABC):
    """Base class for all judges. A judge consumes a TestCase and a candidate
    output string, and returns a Verdict."""

    kind: ClassVar[str] = ""

    def __init__(self, name: str, weight: float = 1.0):
        self.name = name
        self.weight = weight

    @classmethod
    def from_config(cls, config: JudgeConfig) -> "Judge":
        return cls(name=config.name or cls.kind, weight=config.weight, **config.config)

    @abstractmethod
    async def evaluate(self, case: TestCase, candidate_output: str) -> Verdict: ...
