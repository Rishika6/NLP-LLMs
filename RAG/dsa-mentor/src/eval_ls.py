"""Run LangSmith evaluation over the dsa-mentor-evals dataset.

Evaluators:
  - pattern_recall: did the answer mention any expected pattern?
  - no_spoiler: heuristic check that no full solution was leaked.
"""
from __future__ import annotations

import os
import re
from pathlib import Path

from dotenv import load_dotenv
from langsmith import Client
from langsmith.evaluation import evaluate
from langsmith.schemas import Example, Run

from ask import build_chain

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

DATASET_NAME = os.environ.get("LANGSMITH_DATASET", "dsa-mentor-evals")

SPOILER_PATTERNS = [
    re.compile(r"\bdef\s+\w+\s*\("),
    re.compile(r"\bclass\s+Solution\b"),
    re.compile(r"```(?:python|cpp|java|js|ts)"),
    re.compile(r"\bfor\b.*\bin\b.*:\s*\n.*\breturn\b", re.DOTALL),
]


def _answer_text(run: Run) -> str:
    out = run.outputs or {}
    return out.get("output") or out.get("answer") or next(iter(out.values()), "") or ""


def pattern_recall(run: Run, example: Example) -> dict:
    answer = _answer_text(run).lower()
    expected = [p.lower() for p in (example.outputs or {}).get("expected_patterns", [])]
    if not expected:
        return {"key": "pattern_recall", "score": None, "comment": "no expected patterns"}
    hits = [p for p in expected if p in answer]
    return {
        "key": "pattern_recall",
        "score": len(hits) / len(expected),
        "comment": f"matched {hits} of {expected}",
    }


def no_spoiler(run: Run, example: Example) -> dict:
    answer = _answer_text(run)
    leaks = [pat.pattern for pat in SPOILER_PATTERNS if pat.search(answer)]
    return {
        "key": "no_spoiler",
        "score": 0.0 if leaks else 1.0,
        "comment": f"leak signals: {leaks}" if leaks else "clean",
    }


def main() -> None:
    chain = build_chain()

    def target(inputs: dict) -> dict:
        return {"output": chain.invoke(inputs["question"])}

    client = Client()
    if not client.has_dataset(dataset_name=DATASET_NAME):
        raise SystemExit(f"dataset {DATASET_NAME!r} not found — run upload_dataset.py first")

    result = evaluate(
        target,
        data=DATASET_NAME,
        evaluators=[pattern_recall, no_spoiler],
        experiment_prefix="dsa-mentor",
    )
    print(result)


if __name__ == "__main__":
    main()
