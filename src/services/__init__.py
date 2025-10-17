# MCP Services Module (cloud-only)
"""
Servicios del servidor MCP (modo cloud-only).

Este paquete expone únicamente el adaptador de OpenAI en la nube.
"""

from .cloud_openai import (
    OpenAIVectorStore,
    ensure_client,
    embed_texts,
    embed_query,
)

__all__ = [
    'OpenAIVectorStore',
    'ensure_client',
    'embed_texts',
    'embed_query',
] 