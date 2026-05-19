# DSA-Mentor

A personal RAG agent for LeetCode practice. Surfaces patterns and similar problems
**without** revealing solutions. LangChain + Chroma + Anthropic, instrumented for
LangSmith retrieval evals.

> Status: learning project, in progress.

## Layout
```
dsa-mentor/
├── notes/          # personal pattern-intuition notes (markdown)
├── data/           # leetcode.jsonl — problem dump (gitignored if large)
├── evals/          # evals.jsonl — question → expected pattern(s)
├── src/
│   ├── corpus.py        # load notes/ + leetcode.jsonl as Documents
│   ├── index.py         # chunk + embed into local Chroma
│   ├── ask.py           # CLI: no-spoiler LCEL chain
│   ├── upload_dataset.py  # push evals.jsonl to LangSmith
│   └── eval_ls.py       # run pattern_recall + no_spoiler evaluators
└── requirements.txt
```

## Setup
```bash
cd RAG/dsa-mentor
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # then fill in ANTHROPIC_API_KEY, LANGSMITH_API_KEY
```

Add at least one pattern note in `notes/` (a starter `two-pointer.md` is included),
and optionally drop a LeetCode dump at `data/leetcode.jsonl` (one JSON object per
line with at minimum `title`, `difficulty`, `tags`, `content`).

## Run
```bash
# build the Chroma index
python src/index.py

# ask a question
python src/ask.py "Find the longest substring without repeating characters"
```

## Evaluate
```bash
# one-time: push eval examples to LangSmith
python src/upload_dataset.py

# run the experiment
python src/eval_ls.py
```

Evaluators:
- **pattern_recall** — fraction of expected patterns named in the answer.
- **no_spoiler** — heuristic: does the answer contain function defs / code blocks?

## What's intentionally not here yet
- LLM-judged answer quality (planned after the heuristic eval surfaces real failure modes).
- Hybrid retrieval (BM25 + dense). Pure-dense first to get a baseline.
- A web UI. CLI + LangSmith traces are enough for the learning loop.
