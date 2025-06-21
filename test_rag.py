#!/usr/bin/env python3
"""
Script de prueba para el sistema RAG con metadatos de fuente
"""

from rag_core import get_vector_store, get_qa_chain, log

def test_rag_system():
    """Prueba el sistema RAG con preguntas sobre el Proyecto Alpha"""
    
    print("=== PRUEBA DEL SISTEMA RAG CON METADATOS DE FUENTE ===\n")
    
    try:
        # Inicializar el sistema
        log("Inicializando sistema RAG...")
        vector_store = get_vector_store()
        qa_chain = get_qa_chain(vector_store)
        
        # Lista de preguntas de prueba
        preguntas = [
            "¿Cuál es el nombre del proyecto?",
            "¿Quién es la responsable del proyecto?",
            "¿Cuál es el objetivo principal del Proyecto Alpha?",
            "¿Cuál es el estado actual del proyecto?",
            "¿Cuándo se espera finalizar la fórmula química?",
            "¿Qué tipo de material se está desarrollando?"
        ]
        
        # Probar cada pregunta
        for i, pregunta in enumerate(preguntas, 1):
            print(f"Pregunta {i}: {pregunta}")
            print("-" * 50)
            
            try:
                response = qa_chain.invoke({"query": pregunta})
                respuesta = response.get("result", "No se pudo obtener respuesta")
                print(f"Respuesta: {respuesta}")
                
                # Mostrar fuentes si están disponibles
                if "source_documents" in response:
                    print(f"\n📚 Fuentes de información:")
                    for j, doc in enumerate(response["source_documents"], 1):
                        print(f"   {j}. Contenido: {doc.page_content[:100]}...")
                        if hasattr(doc, 'metadata') and doc.metadata:
                            print(f"      Metadatos: {doc.metadata}")
                        print()
                
            except Exception as e:
                print(f"Error: {e}")
            
            print("\n" + "="*60 + "\n")
    
    except Exception as e:
        print(f"Error al inicializar el sistema: {e}")

if __name__ == "__main__":
    test_rag_system() 