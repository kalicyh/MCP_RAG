@echo off
echo === SOLUCIONANDO PROBLEMA DE MCP ===
echo.

echo 1. Activando entorno virtual:
call .venv\Scripts\activate.bat
echo.

echo 2. Verificando que estamos en el entorno virtual:
python --version
echo.

echo 3. Desinstalando MCP si existe:
pip uninstall mcp -y
echo.

echo 4. Instalando MCP nuevamente:
pip install mcp[cli]
echo.

echo 5. Verificando instalacion:
pip show mcp
echo.

echo 6. Probando importacion:
python -c "import mcp; print('MCP funciona correctamente!')"
echo.

echo 7. Probando el servidor:
echo Iniciando servidor (presiona Ctrl+C para detenerlo)...
python rag_server.py
echo.

echo === FIN ===
pause 