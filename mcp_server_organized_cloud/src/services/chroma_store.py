"""
Chroma-backed vector store adapter for the cloud package.

This adapter implements the same minimal interface as OpenAIVectorStore:
- add_texts(texts: list[str], metadatas: list[dict] | None) -> list[str]
- search(query: str, k: int = 5, filter: dict | None = None) -> list[dict]
- get() -> {"documents": list[str], "metadatas": list[dict]}
- persist() -> None

Embeddings are computed via services.cloud_openai.embed_texts/embed_query.
Persistence is handled by Chroma via a persist directory.
"""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

try:
    import chromadb  # type: ignore
    from chromadb.config import Settings  # type: ignore
except Exception as e:  # pragma: no cover
    raise RuntimeError("chromadb package is required when using RAG_BACKEND=CHROMA") from e

from .cloud_openai import embed_texts, embed_query


class ChromaVectorStore:
    def __init__(self, persist_directory: str, collection_name: str = "cloud_collection") -> None:
        self._persist_directory = persist_directory
        os.makedirs(self._persist_directory, exist_ok=True)
        self._client = chromadb.Client(Settings(
            anonymized_telemetry=False,
            is_persistent=True,
            persist_directory=self._persist_directory,
        ))
        self._collection = self._client.get_or_create_collection(name=collection_name)

    def _sanitize_meta(self, m: Dict[str, Any]) -> Dict[str, Any]:
        out: Dict[str, Any] = {}
        for k, v in (m or {}).items():
            if v is None:
                continue
            if isinstance(v, (str, int, float, bool)):
                out[k] = v
            elif isinstance(v, (list, tuple, dict)):
                out[k] = str(v)
            else:
                out[k] = str(v)
        return out

    def add_texts(self, texts: List[str], metadatas: Optional[List[Dict[str, Any]]] = None) -> List[str]:
        if not texts:
            return []
        embs = embed_texts(texts)
        start = self._collection.count()
        ids = [str(i) for i in range(start, start + len(texts))]
        metas = metadatas or [{} for _ in texts]
        metas = [self._sanitize_meta(m) for m in metas]
        self._collection.add(ids=ids, documents=texts, metadatas=metas, embeddings=embs)
        # Persist after write for safety
        try:
            self._client.persist()
        except Exception:
            pass
        return ids

    def search(self, query: str, k: int = 5, filter: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        q = embed_query(query)
        where_arg = filter if (filter and isinstance(filter, dict) and len(filter) > 0) else None
        res = self._collection.query(
            query_embeddings=[q],
            n_results=max(1, k),
            where=where_arg,
            include=["documents", "metadatas", "distances"],
        )
        docs = (res.get("documents") or [[]])[0]
        metas = (res.get("metadatas") or [[]])[0]
        out: List[Dict[str, Any]] = []
        for d, m in zip(docs, metas):
            out.append({"text": d, "metadata": m or {}})
        return out

    def get(self) -> Dict[str, Any]:
        res = self._collection.get()
        return {
            "documents": res.get("documents", []) or [],
            "metadatas": res.get("metadatas", []) or [],
        }

    def persist(self) -> None:
        try:
            self._client.persist()
        except Exception:
            pass
