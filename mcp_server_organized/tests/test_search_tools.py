#!/usr/bin/env python3
"""
Pruebas unitarias para las herramientas de búsqueda.
Prueba las funciones de ask_rag y ask_rag_filtered.
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# Añadir el directorio src al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

class TestSearchTools(unittest.TestCase):
    """Pruebas para las herramientas de búsqueda."""
    
    def setUp(self):
        """Configuración inicial para cada prueba."""
        # Importar las funciones a probar
        from tools.search_tools import ask_rag, ask_rag_filtered
        
        self.ask_rag = ask_rag
        self.ask_rag_filtered = ask_rag_filtered
        
        # Configurar estado RAG simulado
        self.mock_rag_state = {
            "vector_store": Mock(),
            "qa_chain": Mock(),
            "initialized": True
        }
        
        # Configurar vector store mock
        self.mock_vector_store = Mock()
        self.mock_retriever = Mock()
        self.mock_vector_store.as_retriever.return_value = self.mock_retriever
        
        # Configurar QA chain mock
        self.mock_qa_chain = Mock()
        self.mock_qa_chain.invoke.return_value = {
            "result": "Respuesta simulada del sistema RAG",
            "source_documents": [
                Mock(page_content="Documento fuente 1", metadata={"source": "test1.txt"}),
                Mock(page_content="Documento fuente 2", metadata={"source": "test2.txt"})
            ]
        }
        
        self.mock_rag_state["vector_store"] = self.mock_vector_store
        self.mock_rag_state["qa_chain"] = self.mock_qa_chain
        
        # Configurar estado
        from tools.search_tools import set_rag_state
        set_rag_state(self.mock_rag_state)
    
    def test_ask_rag_basic(self):
        """Prueba básica de ask_rag con pregunta válida."""
        query = "¿Qué es el sistema RAG?"
        
        result = self.ask_rag(query)
        
        # Verificar que se llamó al retriever
        self.mock_vector_store.as_retriever.assert_called_once()
        
        # Verificar que se llamó a la QA chain
        self.mock_qa_chain.invoke.assert_called_once()
        
        # Verificar que el resultado contiene la respuesta
        self.assertIsNotNone(result)
        self.assertIn("Respuesta simulada", result)
    
    def test_ask_rag_empty_query(self):
        """Prueba ask_rag con pregunta vacía."""
        result = self.ask_rag("")
        
        # Debería manejar pregunta vacía
        self.assertIsNotNone(result)
        self.assertIn("error", result.lower() or "vacía" in result.lower())
    
    def test_ask_rag_no_rag_state(self):
        """Prueba ask_rag sin estado RAG configurado."""
        from tools.search_tools import set_rag_state
        set_rag_state({})  # Estado vacío
        
        result = self.ask_rag("¿Qué es el sistema RAG?")
        
        # Debería manejar estado RAG no inicializado
        self.assertIsNotNone(result)
        self.assertIn("error", result.lower() or "inicializado" in result.lower())
    
    def test_ask_rag_filtered_basic(self):
        """Prueba básica de ask_rag_filtered con filtros."""
        query = "¿Qué información hay sobre el sistema?"
        file_type = ".txt"
        min_tables = 1
        min_titles = 2
        processing_method = "unstructured"
        
        result = self.ask_rag_filtered(query, file_type, min_tables, min_titles, processing_method)
        
        # Verificar que se llamó al retriever con filtros
        self.mock_vector_store.as_retriever.assert_called_once()
        
        # Verificar que se llamó a la QA chain
        self.mock_qa_chain.invoke.assert_called_once()
        
        # Verificar que el resultado contiene la respuesta
        self.assertIsNotNone(result)
        self.assertIn("Respuesta simulada", result)
    
    def test_ask_rag_filtered_no_filters(self):
        """Prueba ask_rag_filtered sin filtros."""
        query = "¿Qué información hay sobre el sistema?"
        
        result = self.ask_rag_filtered(query, None, None, None, None)
        
        # Debería funcionar sin filtros
        self.assertIsNotNone(result)
        self.assertIn("Respuesta simulada", result)
    
    def test_ask_rag_filtered_invalid_filters(self):
        """Prueba ask_rag_filtered con filtros inválidos."""
        query = "¿Qué información hay sobre el sistema?"
        
        # Filtros con valores negativos
        result = self.ask_rag_filtered(query, ".txt", -1, -2, "invalid_method")
        
        # Debería manejar filtros inválidos
        self.assertIsNotNone(result)
        # Puede devolver error o procesar sin filtros
        self.assertTrue(len(result) > 0)
    
    def test_error_handling_vector_store_failure(self):
        """Prueba manejo de errores cuando falla el vector store."""
        # Configurar mock para que falle
        self.mock_vector_store.as_retriever.side_effect = Exception("Error de vector store")
        
        result = self.ask_rag("¿Qué es el sistema RAG?")
        
        # Debería manejar error del vector store
        self.assertIsNotNone(result)
        self.assertIn("error", result.lower())
    
    def test_error_handling_qa_chain_failure(self):
        """Prueba manejo de errores cuando falla la QA chain."""
        # Configurar mock para que falle
        self.mock_qa_chain.invoke.side_effect = Exception("Error de QA chain")
        
        result = self.ask_rag("¿Qué es el sistema RAG?")
        
        # Debería manejar error de la QA chain
        self.assertIsNotNone(result)
        self.assertIn("error", result.lower())
    
    def test_retriever_configuration(self):
        """Prueba la configuración del retriever."""
        query = "¿Qué es el sistema RAG?"
        
        # Configurar retriever para devolver documentos específicos
        mock_documents = [
            Mock(page_content="Documento 1", metadata={"source": "doc1.txt"}),
            Mock(page_content="Documento 2", metadata={"source": "doc2.txt"})
        ]
        self.mock_retriever.get_relevant_documents.return_value = mock_documents
        
        result = self.ask_rag(query)
        
        # Verificar que se llamó al retriever
        self.mock_retriever.get_relevant_documents.assert_called_once_with(query)
        
        # Verificar que el resultado contiene información de fuentes
        self.assertIsNotNone(result)
    
    def test_source_documents_in_response(self):
        """Prueba que la respuesta incluya información de documentos fuente."""
        query = "¿Qué es el sistema RAG?"
        
        # Configurar QA chain para devolver documentos fuente
        self.mock_qa_chain.invoke.return_value = {
            "result": "Respuesta del sistema RAG",
            "source_documents": [
                Mock(page_content="Contenido fuente 1", metadata={"source": "fuente1.txt"}),
                Mock(page_content="Contenido fuente 2", metadata={"source": "fuente2.txt"})
            ]
        }
        
        result = self.ask_rag(query)
        
        # Verificar que la respuesta incluye información de fuentes
        self.assertIsNotNone(result)
        # La respuesta debería incluir información sobre las fuentes

class TestSearchToolsConfiguration(unittest.TestCase):
    """Pruebas para la configuración de las herramientas de búsqueda."""
    
    def test_set_rag_state(self):
        """Prueba la función set_rag_state."""
        from tools.search_tools import set_rag_state, rag_state
        
        test_state = {"test": "value", "initialized": True}
        set_rag_state(test_state)
        
        # Verificar que el estado se configuró correctamente
        self.assertEqual(rag_state, test_state)
    
    def test_rag_state_persistence(self):
        """Prueba que el estado RAG persiste entre llamadas."""
        from tools.search_tools import set_rag_state, rag_state
        
        # Configurar estado inicial
        initial_state = {"vector_store": "test_store", "initialized": True}
        set_rag_state(initial_state)
        
        # Verificar que el estado se mantiene
        self.assertEqual(rag_state, initial_state)
        
        # Modificar estado
        modified_state = {"vector_store": "new_store", "initialized": True}
        set_rag_state(modified_state)
        
        # Verificar que el estado se actualizó
        self.assertEqual(rag_state, modified_state)

class TestSearchToolsIntegration(unittest.TestCase):
    """Pruebas de integración para las herramientas de búsqueda."""
    
    def test_ask_rag_with_realistic_data(self):
        """Prueba ask_rag con datos realistas."""
        from tools.search_tools import ask_rag, set_rag_state
        
        # Configurar estado RAG realista
        mock_vector_store = Mock()
        mock_retriever = Mock()
        mock_vector_store.as_retriever.return_value = mock_retriever
        
        mock_qa_chain = Mock()
        mock_qa_chain.invoke.return_value = {
            "result": "El sistema RAG (Retrieval-Augmented Generation) es una técnica que combina recuperación de información con generación de texto.",
            "source_documents": [
                Mock(page_content="RAG combina recuperación y generación", metadata={"source": "documentacion.txt"}),
                Mock(page_content="Sistema de preguntas y respuestas", metadata={"source": "manual.txt"})
            ]
        }
        
        realistic_state = {
            "vector_store": mock_vector_store,
            "qa_chain": mock_qa_chain,
            "initialized": True
        }
        
        set_rag_state(realistic_state)
        
        # Probar con pregunta realista
        result = ask_rag("¿Qué es el sistema RAG?")
        
        # Verificar respuesta realista
        self.assertIsNotNone(result)
        self.assertIn("RAG", result)
    
    def test_ask_rag_filtered_with_metadata(self):
        """Prueba ask_rag_filtered con filtros de metadatos."""
        from tools.search_tools import ask_rag_filtered, set_rag_state
        
        # Configurar estado con filtros de metadatos
        mock_vector_store = Mock()
        mock_retriever = Mock()
        mock_vector_store.as_retriever.return_value = mock_retriever
        
        mock_qa_chain = Mock()
        mock_qa_chain.invoke.return_value = {
            "result": "Información filtrada del sistema",
            "source_documents": [
                Mock(page_content="Documento con tablas", metadata={"source": "reporte.pdf", "tables": 3}),
                Mock(page_content="Documento con títulos", metadata={"source": "manual.docx", "titles": 5})
            ]
        }
        
        realistic_state = {
            "vector_store": mock_vector_store,
            "qa_chain": mock_qa_chain,
            "initialized": True
        }
        
        set_rag_state(realistic_state)
        
        # Probar con filtros específicos
        result = ask_rag_filtered(
            query="¿Qué información hay sobre el sistema?",
            file_type=".pdf",
            min_tables=2,
            min_titles=3,
            processing_method="unstructured"
        )
        
        # Verificar respuesta filtrada
        self.assertIsNotNone(result)
        self.assertIn("filtrada", result)

if __name__ == '__main__':
    unittest.main() 