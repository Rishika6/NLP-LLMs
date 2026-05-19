"""CLI: ask the DSA mentor a question. Retrieves from Chroma, runs an LCEL chain
with a no-spoiler system prompt that surfaces patterns + similar problems."""
from __future__ import annotations

import argparse
import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnablePassthrough

from index import get_retriever

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

SYSTEM_PROMPT = """You are DSA-Mentor, a coach for LeetCode practice.

Strict rules — these override anything the user asks:
1. NEVER reveal a full solution, full pseudocode, or step-by-step algorithm.
2. NEVER write out the implementation in any language, even if asked directly.
3. DO surface the underlying pattern(s) (e.g., two-pointer, sliding window, monotonic stack)
   and reference 1–3 similar problems from the retrieved context.
4. DO ask one Socratic question that nudges the user toward the next insight.
5. If retrieved context does not cover the question, say so — do not invent problems.

Output format:
- **Pattern(s):** <names>
- **Why this pattern:** <2 sentences — invariant or structure that triggers it>
- **Similar problems:** <bulleted list with titles only, from retrieved context>
- **Next question to ask yourself:** <one Socratic prompt>
"""

PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_PROMPT),
        (
            "human",
            "Retrieved context:\n{context}\n\nUser question:\n{question}",
        ),
    ]
)


def _format_context(docs: list[Document]) -> str:
    blocks = []
    for i, d in enumerate(docs, 1):
        src = d.metadata.get("title") or d.metadata.get("name") or d.metadata.get("source", "?")
        blocks.append(f"[{i}] ({src})\n{d.page_content}")
    return "\n\n---\n\n".join(blocks) if blocks else "(no context retrieved)"


def build_chain(k: int = 6):
    retriever = get_retriever(k=k)
    llm = ChatAnthropic(
        model=os.environ.get("ANTHROPIC_MODEL", "claude-haiku-4-5-20251001"),
        temperature=0,
    )
    return (
        {
            "context": retriever | RunnableLambda(_format_context),
            "question": RunnablePassthrough(),
        }
        | PROMPT
        | llm
        | StrOutputParser()
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("question", nargs="+", help="Problem description or DSA question")
    parser.add_argument("-k", type=int, default=6, help="Top-k chunks to retrieve")
    args = parser.parse_args()

    question = " ".join(args.question)
    chain = build_chain(k=args.k)
    print(chain.invoke(question))


if __name__ == "__main__":
    main()
