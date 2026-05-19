"""Load the dsa-mentor corpus: personal pattern notes + LeetCode problems."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable

from langchain_core.documents import Document

ROOT = Path(__file__).resolve().parents[1]
NOTES_DIR = ROOT / "notes"
DATA_DIR = ROOT / "data"
LEETCODE_FILE = DATA_DIR / "leetcode.jsonl"


def load_notes() -> list[Document]:
    docs: list[Document] = []
    for md in sorted(NOTES_DIR.glob("*.md")):
        docs.append(
            Document(
                page_content=md.read_text(encoding="utf-8"),
                metadata={"source": str(md.relative_to(ROOT)), "type": "pattern_note", "name": md.stem},
            )
        )
    return docs


def load_leetcode() -> list[Document]:
    if not LEETCODE_FILE.exists():
        return []
    import json

    docs: list[Document] = []
    with LEETCODE_FILE.open() as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            title = row.get("title", "")
            difficulty = row.get("difficulty", "")
            tags = row.get("tags", []) or []
            statement = row.get("content") or row.get("statement") or ""
            body = f"# {title} ({difficulty})\nTags: {', '.join(tags)}\n\n{statement}"
            docs.append(
                Document(
                    page_content=body,
                    metadata={
                        "source": "leetcode",
                        "type": "leetcode_problem",
                        "title": title,
                        "difficulty": difficulty,
                        "tags": tags,
                    },
                )
            )
    return docs


def load_all() -> list[Document]:
    return load_notes() + load_leetcode()


if __name__ == "__main__":
    docs = load_all()
    notes = sum(1 for d in docs if d.metadata.get("type") == "pattern_note")
    problems = sum(1 for d in docs if d.metadata.get("type") == "leetcode_problem")
    print(f"loaded {len(docs)} documents — {notes} pattern notes, {problems} leetcode problems")
