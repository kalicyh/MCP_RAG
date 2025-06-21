@echo off
echo === DIAGNOSTICO DEL ENTORNO VIRTUAL ===
echo.

echo 1. Verificando Python actual:
python --version
echo.

echo 2. Verificando ubicacion de Python:
where python
echo.

echo 3. Verificando pip:
pip --version
echo.

echo 4. Verificando si MCP esta instalado:
pip show mcp
echo.

echo 5. Intentando instalar MCP:
pip install mcp[cli] --force-reinstall
echo.

echo 6. Verificando instalacion de MCP:
pip show mcp
echo.

echo 7. Probando importacion de MCP:
python -c "import mcp; print('MCP importado exitosamente')"
echo.

echo === FIN DEL DIAGNOSTICO ===
pause 