#!/usr/bin/env python3
"""
Script de lanzamiento para la aplicación GUI de Bulk Ingest
"""

import sys
import os
import subprocess

def check_dependencies():
    """Verificar que todas las dependencias estén instaladas"""
    try:
        import tkinter
        print("✅ Tkinter está disponible")
    except ImportError:
        print("❌ Error: Tkinter no está instalado")
        print("En Ubuntu/Debian: sudo apt-get install python3-tk")
        print("En CentOS/RHEL: sudo yum install tkinter")
        print("En Windows: tkinter viene incluido con Python")
        return False
    
    try:
        from markitdown import MarkItDown
        print("✅ MarkItDown está disponible")
    except ImportError:
        print("❌ Error: MarkItDown no está instalado")
        print("Ejecuta: pip install markitdown")
        return False
    
    try:
        from rag_core import get_vector_store, add_text_to_knowledge_base
        print("✅ RAG Core está disponible")
    except ImportError:
        print("❌ Error: RAG Core no está disponible")
        print("Asegúrate de estar en el directorio correcto del proyecto")
        return False
    
    return True

def main():
    """Función principal"""
    print("🚀 Iniciando Bulk Ingest GUI...")
    print("=" * 50)
    
    # Verificar dependencias
    if not check_dependencies():
        print("\n❌ No se pueden verificar todas las dependencias")
        input("Presiona Enter para salir...")
        sys.exit(1)
    
    print("\n✅ Todas las dependencias están disponibles")
    print("🎯 Iniciando interfaz gráfica...\n")
    
    try:
        # Importar y ejecutar la GUI
        from bulk_ingest_gui import main as gui_main
        gui_main()
    except Exception as e:
        print(f"❌ Error al iniciar la GUI: {e}")
        print("\n💡 Posibles soluciones:")
        print("1. Verifica que estés en el directorio correcto del proyecto")
        print("2. Asegúrate de que todas las dependencias estén instaladas")
        print("3. Revisa que el archivo bulk_ingest_gui.py exista")
        input("\nPresiona Enter para salir...")
        sys.exit(1)

if __name__ == "__main__":
    main() 