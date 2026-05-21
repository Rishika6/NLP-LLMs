"""CLI: ask the DSA mentor a question. Retrieves from Chroma, runs an LCEL chain
with a no-spoiler system prompt that surfaces patterns + similar problems."""
from __future__ import annotations

import argparse
import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint

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

EXAMPLE_USER = """Retrieved context:
[1] (kadanes-algorithm)
# Kadane's Algorithm

## When to reach for it
- You want a single O(n) sweep over an array tracking a "best so far" value.
- The problem asks for an optimal contiguous range (max sum, min sum, etc.).

## The invariant
At each index i, you carry forward either (a) the running candidate extended by arr[i], or (b) a fresh start at arr[i] — whichever is larger. The local optimum at i depends only on the local optimum at i-1.

[2] (Maximum Subarray)
# Maximum Subarray (Medium)
Tags: array, dynamic-programming

Given an integer array nums, find the contiguous subarray with the largest sum and return its sum.

[3] (Maximum Product Subarray)
# Maximum Product Subarray (Medium)
Tags: array, dynamic-programming

Given an integer array nums, find a contiguous subarray that has the largest product.

User question:
Given an array of integers, find the contiguous subarray with the largest sum."""

EXAMPLE_ASSISTANT = """- **Pattern(s):** Kadane's algorithm / dynamic programming
- **Why this pattern:** The best subarray ending at index i is either the best subarray ending at i-1 extended by nums[i], or just nums[i] starting fresh — a single local decision per index. That structure turns an O(n^2) brute force into a linear sweep.
- **Similar problems:**
  - Maximum Subarray
  - Maximum Product Subarray
- **Next question to ask yourself:** What changes about the "extend vs. restart" decision when the array can contain negative numbers, and does the same invariant still hold for the *product* version?"""

PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_PROMPT),
        ("human", EXAMPLE_USER),
        ("ai", EXAMPLE_ASSISTANT),
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
    endpoint = HuggingFaceEndpoint(
        repo_id=os.environ.get("HF_MODEL", "meta-llama/Llama-3.3-70B-Instruct"),
        task="text-generation",
        max_new_tokens=512,
        do_sample=False,
        huggingfacehub_api_token=os.environ["HF_TOKEN"],
    )
    llm = ChatHuggingFace(llm=endpoint)
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
