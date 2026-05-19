"""Push evals/evals.jsonl into a LangSmith dataset for retrieval + answer evals."""
from __future__ import annotations

import json
import os
from pathlib import Path

from dotenv import load_dotenv
from langsmith import Client

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

EVALS_FILE = ROOT / "evals" / "evals.jsonl"
DATASET_NAME = os.environ.get("LANGSMITH_DATASET", "dsa-mentor-evals")


def main() -> None:
    if not EVALS_FILE.exists():
        raise SystemExit(f"missing {EVALS_FILE}")

    client = Client()
    if client.has_dataset(dataset_name=DATASET_NAME):
        ds = client.read_dataset(dataset_name=DATASET_NAME)
        print(f"reusing dataset {DATASET_NAME} ({ds.id})")
    else:
        ds = client.create_dataset(
            dataset_name=DATASET_NAME,
            description="DSA-Mentor: question → expected pattern(s) + acceptable similar problems",
        )
        print(f"created dataset {DATASET_NAME} ({ds.id})")

    examples = []
    with EVALS_FILE.open() as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            examples.append(
                {
                    "inputs": {"question": row["question"]},
                    "outputs": {
                        "expected_patterns": row["expected_patterns"],
                        "expected_similar": row.get("expected_similar", []),
                    },
                }
            )

    client.create_examples(
        inputs=[e["inputs"] for e in examples],
        outputs=[e["outputs"] for e in examples],
        dataset_id=ds.id,
    )
    print(f"uploaded {len(examples)} examples")


if __name__ == "__main__":
    main()
