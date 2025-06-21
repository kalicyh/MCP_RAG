@echo off
rem Este script establece el entorno de codificación a UTF-8 y lanza el servidor MCP.
rem Esto previene errores de codificación en Windows.

set PYTHONUTF8=1
D:\\MCP_RAG\\.venv\\Scripts\\python.exe D:\\MCP_RAG\\rag_server.py 