"""Chunk the corpus and embed it into a local Chroma store."""
from __future__ import annotations

from pathlib import Path

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from corpus import load_all

ROOT = Path(__file__).resolve().parents[1]
CHROMA_DIR = ROOT / "chroma"
COLLECTION = "dsa-mentor"
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


def build_index() -> None:
    docs = load_all()
    if not docs:
        raise SystemExit("corpus is empty — add notes/*.md or data/leetcode.jsonl first")

    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=120)
    chunks = splitter.split_documents(docs)

    embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL)
    Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name=COLLECTION,
        persist_directory=str(CHROMA_DIR),
    )
    print(f"indexed {len(chunks)} chunks from {len(docs)} docs into {CHROMA_DIR}")


def get_retriever(k: int = 6):
    embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL)
    store = Chroma(
        collection_name=COLLECTION,
        embedding_function=embeddings,
        persist_directory=str(CHROMA_DIR),
    )
    return store.as_retriever(search_kwargs={"k": k})


if __name__ == "__main__":
    build_index()
