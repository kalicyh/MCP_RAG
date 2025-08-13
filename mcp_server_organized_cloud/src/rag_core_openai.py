"""
Cloud-only RAG core using OpenAI APIs and an in-memory vector store.

This file replaces langchain/chroma/unstructured with minimal logic:
- Vector store: services.cloud_openai.OpenAIVectorStore
- QA chain: OpenAI chat completion over top-k retrieved chunks
- Document loading: simple text reader fallback
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

try:
    from utils.logger import log
except Exception:
    def log(msg: str):
        print(msg)

from services.cloud_openai import (
    OpenAIVectorStore,
    ensure_client,
    embed_query,
)


_VECTOR_STORE: Optional[OpenAIVectorStore] = None


def get_vector_store(profile: str = 'auto') -> OpenAIVectorStore:
    global _VECTOR_STORE
    if _VECTOR_STORE is None:
        _VECTOR_STORE = OpenAIVectorStore()
        log("核心: 已初始化 OpenAI 内存向量库 (cloud-only)")
    return _VECTOR_STORE


def _chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    if not text:
        return []
    chunks: List[str] = []
    start = 0
    n = len(text)
    while start < n:
        end = min(start + chunk_size, n)
        chunks.append(text[start:end])
        if end == n:
            break
        start = max(end - overlap, 0)
    return chunks


def flatten_metadata(metadata: Dict[str, Any], prefix: str = "") -> Dict[str, Any]:
    flat: Dict[str, Any] = {}
    for k, v in (metadata or {}).items():
        key = f"{prefix}{k}" if prefix else k
        if isinstance(v, dict):
            flat.update(flatten_metadata(v, f"{key}_"))
        elif isinstance(v, (list, tuple)):
            flat[key] = str(v)
        else:
            flat[key] = v
    return flat


def add_text_to_knowledge_base_enhanced(
    text: str,
    vector_store: OpenAIVectorStore,
    source_metadata: Optional[dict] = None,
    use_semantic_chunking: bool = False,
    structural_elements: Optional[List[Any]] = None,
) -> None:
    if not text or text.isspace():
        log("核心警告: 空文本，忽略")
        return
    # simple chunking
    texts = _chunk_text(text, 1000, 200)
    metadatas: Optional[List[Dict[str, Any]]] = None
    if source_metadata:
        metadatas = []
        for i in range(len(texts)):
            m = flatten_metadata(source_metadata)
            m["chunk_index"] = i
            m["total_chunks"] = len(texts)
            m["chunking_method"] = "standard" if not use_semantic_chunking else "semantic"
            metadatas.append(m)
    vector_store.add_texts(texts, metadatas=metadatas)
    log(f"核心: 已写入 {len(texts)} 个片段到内存向量库")


def add_text_to_knowledge_base(text: str, vector_store: OpenAIVectorStore, source_metadata: dict | None = None) -> None:
    add_text_to_knowledge_base_enhanced(text, vector_store, source_metadata, use_semantic_chunking=False)


def create_metadata_filter(
    file_type: str | None = None,
    processing_method: str | None = None,
    min_tables: int | None = None,
    min_titles: int | None = None,
    source_contains: str | None = None,
) -> dict:
    conditions: List[dict] = []
    if file_type:
        conditions.append({"file_type": file_type})
    if processing_method:
        conditions.append({"processing_method": processing_method})
    if min_tables is not None:
        conditions.append({"structural_info_tables_count": {"$gte": min_tables}})
    if min_titles is not None:
        conditions.append({"structural_info_titles_count": {"$gte": min_titles}})
    if not conditions:
        return {}
    if len(conditions) == 1:
        return conditions[0]
    return {"$and": conditions}


@dataclass
class SimpleDocument:
    page_content: str
    metadata: Dict[str, Any]


class QAChain:
    def __init__(self, vector_store: OpenAIVectorStore, metadata_filter: Optional[dict] = None):
        self.vs = vector_store
        self.filter = metadata_filter

    def invoke(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        query = inputs.get("query", "")
        top = self.vs.search(query, k=5, filter=self.filter)
        context = "\n\n".join([x["text"][:1200] for x in top])
        client = ensure_client()
        model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
        msgs = [
            {"role": "system", "content": "You are a helpful assistant. Answer strictly based on the provided context."},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"},
        ]
        try:
            resp = client.chat.completions.create(model=model, messages=msgs, temperature=float(os.environ.get("OPENAI_TEMPERATURE", "0")))
            answer = resp.choices[0].message.content or ""
        except Exception as e:
            answer = f"[OpenAI 调用失败] {e}"
        sources = [SimpleDocument(page_content=r["text"], metadata=r["metadata"]) for r in top]
        return {"result": answer, "source_documents": sources}


def get_qa_chain(vector_store: OpenAIVectorStore, metadata_filter: dict | None = None) -> QAChain:
    return QAChain(vector_store, metadata_filter)


def search_with_metadata_filters(vector_store: OpenAIVectorStore, query: str, metadata_filter: dict | None = None, k: int = 5) -> List[SimpleDocument]:
    results = vector_store.search(query, k=k, filter=metadata_filter)
    return [SimpleDocument(page_content=r["text"], metadata=r["metadata"]) for r in results]


def get_document_statistics(vector_store: OpenAIVectorStore | None = None) -> dict:
    vs = vector_store or get_vector_store()
    total = len(vs._metas)
    file_types: Dict[str, int] = {}
    methods: Dict[str, int] = {}
    structural = {
        "documents_with_tables": 0,
        "documents_with_lists": 0,
        "documents_with_titles": 0,
        "avg_tables_per_doc": 0,
        "avg_titles_per_doc": 0,
        "avg_lists_per_doc": 0,
    }
    sum_tables = sum_titles = sum_lists = 0
    for m in vs._metas:
        ft = m.get("file_type", "unknown")
        file_types[ft] = file_types.get(ft, 0) + 1
        pm = m.get("processing_method", "unknown")
        methods[pm] = methods.get(pm, 0) + 1
        t = int(m.get("structural_info_tables_count", 0) or 0)
        ti = int(m.get("structural_info_titles_count", 0) or 0)
        l = int(m.get("structural_info_lists_count", 0) or 0)
        if t > 0:
            structural["documents_with_tables"] += 1
        if ti > 0:
            structural["documents_with_titles"] += 1
        if l > 0:
            structural["documents_with_lists"] += 1
        sum_tables += t
        sum_titles += ti
        sum_lists += l
    if total > 0:
        structural["avg_tables_per_doc"] = sum_tables / total
        structural["avg_titles_per_doc"] = sum_titles / total
        structural["avg_lists_per_doc"] = sum_lists / total
    return {
        "total_documents": total,
        "file_types": file_types,
        "processing_methods": methods,
        "structural_stats": structural,
    }


def get_vector_store_stats(vector_store: OpenAIVectorStore | None = None) -> dict:
    vs = vector_store or get_vector_store()
    try:
        dim = len(embed_query("__probe__"))
    except Exception:
        dim = "unknown"
    return {
        "total_documents": len(vs._metas),
        "file_types": {},
        "processing_methods": {},
        "collection_name": "openai_in_memory",
        "embedding_dimension": str(dim),
    }


def optimize_vector_store(vector_store: OpenAIVectorStore | None = None) -> dict:
    return {"status": "success", "message": "no-op for in-memory store"}


def reindex_vector_store(vector_store: OpenAIVectorStore | None = None, profile: str = 'auto') -> dict:
    return {"status": "success", "message": "no-op for in-memory store", "profile": profile}


def load_document_with_fallbacks(file_path: str) -> tuple[str, dict]:
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except Exception as e:
        log(f"核心警告: 读取文件失败: {e}")
        content = ""
    metadata = {
        "source": os.path.basename(file_path),
        "file_path": file_path,
        "file_type": os.path.splitext(file_path)[1].lower(),
        "processed_date": datetime.now().isoformat(),
        "processing_method": "simple_loader",
        "structural_info": {
            "total_elements": 1,
            "titles_count": 0,
            "tables_count": 0,
            "lists_count": 0,
            "narrative_blocks": 1,
            "other_elements": 0,
            "total_text_length": len(content),
            "avg_element_length": len(content),
        },
    }
    return content, metadata


def load_document_with_elements(file_path: str) -> tuple[str, dict, List[Any]]:
    content, metadata = load_document_with_fallbacks(file_path)
    return content, metadata, []


# Cache stubs

def get_cache_stats() -> Dict[str, Any]:
    return {
        "total_requests": 0,
        "memory_hits": 0,
        "disk_hits": 0,
        "misses": 0,
        "memory_hit_rate": "0%",
        "disk_hit_rate": "0%",
        "overall_hit_rate": "0%",
        "memory_cache_size": 0,
        "max_memory_size": 0,
        "cache_directory": "",
    }


def print_cache_stats() -> None:
    log("缓存统计: 不适用（cloud-only 最简实现）")


def clear_embedding_cache() -> None:
    log("已清空缓存（无实际缓存，cloud-only 最简实现）")


def get_optimal_vector_store_profile() -> str:
    return "small"
