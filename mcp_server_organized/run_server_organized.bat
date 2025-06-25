@echo off
rem Script para ejecutar el servidor MCP organizado
rem Establece el entorno de codificación a UTF-8 y lanza el servidor MCP organizado.

set PYTHONUTF8=1
set PYTHONPATH=D:\MCP_RAG\mcp_server_organized\src

D:\MCP_RAG\.venv\Scripts\python.exe D:\MCP_RAG\mcp_server_organized\server.py 