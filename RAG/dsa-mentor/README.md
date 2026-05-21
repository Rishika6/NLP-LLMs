# DSA-Mentor

A personal RAG agent for LeetCode practice. Surfaces **patterns and similar problems
without revealing solutions** — so you keep doing the thinking. Instrumented with
LangSmith so retrieval and answer quality can be evaluated, not just vibed.

> Status: learning project, in progress.

## Stack

| Component | Choice |
|-----------|--------|
| LLM (answer generation) | `meta-llama/Llama-3.3-70B-Instruct` via Hugging Face Inference API |
| Embeddings | `sentence-transformers/all-MiniLM-L6-v2` (local, CPU) |
| Vector store | Chroma (local, persisted on disk) |
| Orchestration | LangChain (LCEL) |
| Evals & tracing | LangSmith (optional) |

The LLM is swappable via the `HF_MODEL` env var without code changes — see [Swapping models](#swapping-models) below.

## Layout

```
dsa-mentor/
├── notes/          # personal pattern-intuition notes (markdown)
├── data/           # leetcode.jsonl — problem dump (gitignored if large)
├── evals/          # evals.jsonl — question → expected pattern(s)
├── chroma/         # persisted vector index (gitignored, built by index.py)
├── src/
│   ├── corpus.py          # load notes/ + leetcode.jsonl as Documents
│   ├── index.py           # chunk + embed into local Chroma
│   ├── ask.py             # CLI: no-spoiler LCEL chain
│   ├── upload_dataset.py  # push evals.jsonl to LangSmith
│   └── eval_ls.py         # run pattern_recall + no_spoiler evaluators
├── requirements.txt
└── .env.example
```

## Setup

### 1. Get a Hugging Face token

- Create one at https://huggingface.co/settings/tokens (a "Read" token is enough).
- Accept the Llama 3.3 license once at https://huggingface.co/meta-llama/Llama-3.3-70B-Instruct (instant — just click *Agree*). Skip if you plan to use an ungated model like `Qwen/Qwen2.5-72B-Instruct`.

### 2. Install

```bash
cd RAG/dsa-mentor
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
chmod 600 .env
```

Then open `.env` and fill in:

```
HF_TOKEN=hf_...                # required
HF_MODEL=meta-llama/Llama-3.3-70B-Instruct   # optional; default shown
LANGSMITH_API_KEY=...          # optional, only needed for `eval_ls.py`
LANGSMITH_TRACING=true
LANGSMITH_PROJECT=dsa-mentor
```

`.env` is gitignored — never commit it.

### 3. Add corpus content

Add at least one pattern note in `notes/` (starter `two-pointer.md` is included),
and optionally drop a LeetCode dump at `data/leetcode.jsonl` (one JSON object per
line with at minimum `title`, `difficulty`, `tags`, `content`).

## Run

```bash
# build the Chroma index (first run downloads ~80MB embedding model)
python src/index.py

# ask a question
python src/ask.py "Find the longest substring without repeating characters"
```

Expected output is a structured response: `Pattern(s)`, `Why this pattern`,
`Similar problems`, `Next question to ask yourself` — no code, no algorithm
walkthrough.

## Swapping models

The default is Llama 3.3 70B. Override per-invocation:

```bash
HF_MODEL="Qwen/Qwen2.5-72B-Instruct" python src/ask.py "..."
HF_MODEL="mistralai/Mistral-Large-Instruct-2411" python src/ask.py "..."
```

Or change the default in `.env`. Any chat model on HF Inference Providers works
as long as it supports the chat-completions interface.

## Evaluate

```bash
# one-time: push eval examples to LangSmith
python src/upload_dataset.py

# run the experiment
python src/eval_ls.py
```

Evaluators:

- **pattern_recall** — fraction of expected patterns named in the answer.
- **no_spoiler** — heuristic: does the answer contain function defs or code blocks?

Results land in your LangSmith project under the `dsa-mentor` experiment prefix.

## What's intentionally not here yet

- LLM-judged answer quality (planned after the heuristic eval surfaces real failure modes).
- Hybrid retrieval (BM25 + dense). Pure-dense first to get a baseline.
- A web UI. CLI + LangSmith traces are enough for the learning loop.
