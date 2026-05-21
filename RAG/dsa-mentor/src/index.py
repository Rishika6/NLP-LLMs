"""Chunk the corpus and embed it into a local Chroma store."""
from __future__ import annotations

from pathlib import Path

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter

from corpus import load_all

ROOT = Path(__file__).resolve().parents[1]
CHROMA_DIR = ROOT / "chroma"
COLLECTION = "dsa-mentor"
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

CHUNK_SIZE = 800
CHUNK_OVERLAP = 120
MARKDOWN_HEADERS = [("#", "h1"), ("##", "h2"), ("###", "h3")]


def _split_note(doc: Document) -> list[Document]:
    header_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=MARKDOWN_HEADERS,
        strip_headers=False,
    )
    sections = header_splitter.split_text(doc.page_content)
    for s in sections:
        s.metadata = {**doc.metadata, **s.metadata}

    char_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP
    )
    return char_splitter.split_documents(sections)


def _split_problem(doc: Document) -> list[Document]:
    char_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP
    )
    return char_splitter.split_documents([doc])


def chunk_corpus(docs: list[Document]) -> list[Document]:
    chunks: list[Document] = []
    for d in docs:
        if d.metadata.get("type") == "pattern_note":
            chunks.extend(_split_note(d))
        else:
            chunks.extend(_split_problem(d))
    return chunks


def build_index() -> None:
    docs = load_all()
    if not docs:
        raise SystemExit("corpus is empty — add notes/*.md or data/leetcode.jsonl first")

    chunks = chunk_corpus(docs)

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
