from __future__ import annotations

from pathlib import Path

import yaml

from evalkit.types import TestCase


def load_dataset(path: str | Path) -> list[TestCase]:
    """Load test cases from a YAML file.

    The file is expected to contain either a top-level list of cases,
    or a mapping with a 'cases' key.
    """
    path = Path(path)
    with path.open(encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    if isinstance(raw, dict):
        raw_cases = raw.get("cases", [])
        default_judges = raw.get("default_judges", [])
    else:
        raw_cases = raw
        default_judges = []

    cases: list[TestCase] = []
    for entry in raw_cases:
        if "judges" not in entry and default_judges:
            entry = {**entry, "judges": default_judges}
        cases.append(TestCase.model_validate(entry))
    return cases
