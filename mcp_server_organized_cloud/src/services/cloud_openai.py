"""
OpenAI Cloud adapter (minimal): vector store + embeddings + file parsing.

This module provides a small wrapper over OpenAI's APIs to support a
cloud-only RAG flow without local vector DBs or local parsers.

Contract:
- class OpenAIVectorStore:
    - add_texts(texts: list[str], metadatas: list[dict] | None) -> list[str]
    - search(query: str, k: int = 5, filter: dict | None = None) -> list[dict]
      Each result dict: {"text": str, "metadata": dict}
- functions:
    - ensure_client() -> OpenAI client
    - embed_texts(texts: list[str]) -> list[list[float]]
    - embed_query(text: str) -> list[float]

Note: For simplicity, this keeps an in-memory list as a fallback store.
In production, replace with OpenAI Vector Stores API (files + chunks + search).
"""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional
import json
from pathlib import Path
import locale

try:
    from openai import OpenAI
except Exception as e:  # pragma: no cover
    raise RuntimeError("openai package is required for cloud-only mode") from e


_client: Optional[OpenAI] = None


def ensure_client() -> OpenAI:
    global _client
    if _client is None:
        api_key = os.environ.get("OPENAI_API_KEY")
        base_url = os.environ.get("OPENAI_API_BASE", "https://api.openai.com/v1")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is not set")
        _client = OpenAI(api_key=api_key, base_url=base_url)
    return _client


def _embedding_model() -> str:
    return os.environ.get("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")


def embed_texts(texts: List[str]) -> List[List[float]]:
    client = ensure_client()
    if not texts:
        return []
    resp = client.embeddings.create(model=_embedding_model(), input=texts)
    # The SDK returns data in resp.data with .embedding attributes
    return [d.embedding for d in resp.data]


def embed_query(text: str) -> List[float]:
    vecs = embed_texts([text])
    return vecs[0] if vecs else []


class OpenAIVectorStore:
    """
    Minimal in-memory vector store backed by OpenAI embeddings.
    Replace with OpenAI Vector Stores API when ready.
    """

    def __init__(self) -> None:
        self._texts: List[str] = []
        self._metas: List[Dict[str, Any]] = []
        self._embs: List[List[float]] = []

    # compatibility with previous code using .add_texts
    def add_texts(self, texts: List[str], metadatas: Optional[List[Dict[str, Any]]] = None) -> List[str]:
        if not texts:
            return []
        embs = embed_texts(texts)
        ids = []
        for i, t in enumerate(texts):
            self._texts.append(t)
            self._embs.append(embs[i])
            self._metas.append((metadatas[i] if metadatas and i < len(metadatas) else {}) or {})
            ids.append(str(len(self._texts) - 1))
        return ids

    # simple cosine similarity
    @staticmethod
    def _cosine(a: List[float], b: List[float]) -> float:
        import math
        if not a or not b or len(a) != len(b):
            return -1.0
        dot = sum(x * y for x, y in zip(a, b))
        na = math.sqrt(sum(x * x for x in a))
        nb = math.sqrt(sum(y * y for y in b))
        if na == 0 or nb == 0:
            return -1.0
        return dot / (na * nb)

    def search(self, query: str, k: int = 5, filter: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        q = embed_query(query)
        scored = []
        for i, e in enumerate(self._embs):
            meta = self._metas[i]
            if filter and not _meta_match(meta, filter):
                continue
            scored.append((self._cosine(q, e), i))
        scored.sort(key=lambda x: x[0], reverse=True)
        results: List[Dict[str, Any]] = []
        for _, idx in scored[:k]:
            results.append({"text": self._texts[idx], "metadata": self._metas[idx]})
        return results

    # compatibility helper for stats code used by utility tools
    def get(self) -> Dict[str, Any]:
        return {
            "documents": list(self._texts),
            "metadatas": list(self._metas),
        }

    # --- Persistence helpers ---
    def save_to_file(self, file_path: str) -> None:
        try:
            p = Path(file_path)
            p.parent.mkdir(parents=True, exist_ok=True)
            data = {
                "texts": self._texts,
                "metas": self._metas,
                "embs": self._embs,
            }
            # 始终使用 UTF-8 写入，避免平台默认编码不一致导致后续读取失败
            p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception as e:
            # persistence should be best-effort; avoid crashing
            try:
                from utils.logger import log
                log(f"持久化保存失败: {e}")
            except Exception:
                pass

    def load_from_file(self, file_path: str) -> int:
        try:
            p = Path(file_path)
            if not p.exists():
                return 0
            # 优先按 UTF-8 读取；如失败则回退到系统首选编码以兼容历史文件
            try:
                raw = p.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                enc = locale.getpreferredencoding(False) or "utf-8"
                raw = p.read_text(encoding=enc, errors="replace")
            data = json.loads(raw)
            self._texts = list(data.get("texts", []))
            self._metas = list(data.get("metas", []))
            self._embs = list(data.get("embs", []))
            return len(self._texts)
        except Exception as e:
            try:
                from utils.logger import log
                log(f"持久化加载失败: {e}")
            except Exception:
                pass
            return 0


def _meta_match(meta: Dict[str, Any], flt: Dict[str, Any]) -> bool:
    # Minimal filter matcher supporting {key: value} and {"$and": [..]}
    if not flt:
        return True
    if "$and" in flt:
        return all(_meta_match(meta, c) for c in flt["$and"])
    for k, v in flt.items():
        if k == "$and":
            continue
        mv = meta.get(k)
        if isinstance(v, dict) and "$gte" in v:
            try:
                if (mv is None) or (float(mv) < float(v["$gte"])):
                    return False
            except Exception:
                return False
        else:
            if mv != v:
                return False
    return True
