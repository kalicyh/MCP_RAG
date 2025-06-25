#!/usr/bin/env python3
"""
Test Interactivo del Servidor MCP
=================================

Este script permite probar interactivamente las herramientas del servidor MCP
desde tu editor.
"""

import sys
import os

# Añadir el directorio src al path
sys.path.insert(0, 'src')

def interactive_test():
    """Test interactivo del servidor MCP."""
    
    print("🚀 **TEST INTERACTIVO DEL SERVIDOR MCP**")
    print("=" * 50)
    
    try:
        # Importar el servidor
        from server import mcp
        print("✅ Servidor MCP cargado correctamente")
        
        while True:
            print("\n" + "="*50)
            print("OPCIONES DISPONIBLES:")
            print("1. Añadir texto (learn_text)")
            print("2. Ver estadísticas (get_knowledge_base_stats)")
            print("3. Hacer pregunta (ask_rag)")
            print("4. Ver cache de embeddings (get_embedding_cache_stats)")
            print("5. Limpiar cache (clear_embedding_cache_tool)")
            print("6. Salir")
            print("="*50)
            
            choice = input("\nSelecciona una opción (1-6): ").strip()
            
            if choice == "1":
                text = input("Ingresa el texto a añadir: ")
                result = mcp.learn_text(text)
                print(f"\nResultado: {result}")
                
            elif choice == "2":
                stats = mcp.get_knowledge_base_stats()
                print(f"\nEstadísticas:\n{stats}")
                
            elif choice == "3":
                question = input("Ingresa tu pregunta: ")
                answer = mcp.ask_rag(question)
                print(f"\nRespuesta:\n{answer}")
                
            elif choice == "4":
                cache_stats = mcp.get_embedding_cache_stats()
                print(f"\nEstadísticas del cache:\n{cache_stats}")
                
            elif choice == "5":
                result = mcp.clear_embedding_cache_tool()
                print(f"\nResultado: {result}")
                
            elif choice == "6":
                print("👋 ¡Hasta luego!")
                break
                
            else:
                print("❌ Opción no válida. Intenta de nuevo.")
                
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    interactive_test() 