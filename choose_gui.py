#!/usr/bin/env python3
"""
Script para elegir entre la versión básica y avanzada de Bulk Ingest GUI
"""

import sys
import os
import subprocess

def print_banner():
    """Imprimir banner de bienvenida"""
    print("=" * 60)
    print("🚀 BULK INGEST GUI - SELECTOR DE VERSIÓN")
    print("=" * 60)
    print()

def print_version_info():
    """Mostrar información de las versiones disponibles"""
    print("📋 VERSIONES DISPONIBLES:")
    print()
    
    print("1️⃣  VERSIÓN BÁSICA (bulk_ingest_gui.py)")
    print("   ✅ Procesamiento directo a base de datos")
    print("   ✅ Interfaz simple y rápida")
    print("   ✅ Barra de progreso en tiempo real")
    print("   ✅ Logs detallados")
    print("   ⚡ Ideal para: Procesamiento rápido sin revisión")
    print()
    
    print("2️⃣  VERSIÓN AVANZADA (bulk_ingest_gui_advanced.py)")
    print("   ✅ Previsualización de documentos en Markdown")
    print("   ✅ Selección de documentos antes de almacenar")
    print("   ✅ Interfaz con pestañas organizadas")
    print("   ✅ Control de calidad del contenido")
    print("   ✅ Navegación entre documentos")
    print("   🎯 Ideal para: Revisión y control de calidad")
    print()

def check_dependencies():
    """Verificar dependencias básicas"""
    try:
        import tkinter
        print("✅ Tkinter está disponible")
    except ImportError:
        print("❌ Error: Tkinter no está instalado")
        print("En Ubuntu/Debian: sudo apt-get install python3-tk")
        print("En CentOS/RHEL: sudo yum install tkinter")
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

def run_basic_version():
    """Ejecutar versión básica"""
    print("🚀 Iniciando versión básica...")
    try:
        from bulk_ingest_gui import main as gui_main
        gui_main()
    except Exception as e:
        print(f"❌ Error al iniciar versión básica: {e}")
        input("Presiona Enter para continuar...")

def run_advanced_version():
    """Ejecutar versión avanzada"""
    print("🚀 Iniciando versión avanzada...")
    try:
        from bulk_ingest_gui_advanced import main as gui_main
        gui_main()
    except Exception as e:
        print(f"❌ Error al iniciar versión avanzada: {e}")
        input("Presiona Enter para continuar...")

def main():
    """Función principal"""
    print_banner()
    
    # Verificar dependencias
    print("🔍 Verificando dependencias...")
    if not check_dependencies():
        print("\n❌ No se pueden verificar todas las dependencias")
        input("Presiona Enter para salir...")
        sys.exit(1)
    
    print("✅ Todas las dependencias están disponibles\n")
    
    # Mostrar información de versiones
    print_version_info()
    
    # Menú de selección
    while True:
        print("🎯 ¿QUÉ VERSIÓN QUIERES USAR?")
        print("1. Versión Básica (Procesamiento directo)")
        print("2. Versión Avanzada (Con previsualización)")
        print("3. Ver documentación")
        print("4. Salir")
        print()
        
        choice = input("Ingresa tu elección (1-4): ").strip()
        
        if choice == "1":
            print("\n" + "="*50)
            run_basic_version()
            break
        elif choice == "2":
            print("\n" + "="*50)
            run_advanced_version()
            break
        elif choice == "3":
            print("\n📚 DOCUMENTACIÓN DISPONIBLE:")
            print("📖 GUI_README.md - Documentación versión básica")
            print("📖 GUI_ADVANCED_README.md - Documentación versión avanzada")
            print()
            input("Presiona Enter para continuar...")
            print()
        elif choice == "4":
            print("\n👋 ¡Hasta luego!")
            break
        else:
            print("\n❌ Opción no válida. Por favor ingresa 1, 2, 3 o 4.")
            print()

if __name__ == "__main__":
    main() 