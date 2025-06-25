#!/usr/bin/env python3
"""
Pruebas unitarias para las herramientas de procesamiento de documentos.
Prueba las funciones de learn_text, learn_document y learn_from_url.
"""

import unittest
import tempfile
import os
import sys
from unittest.mock import Mock, patch, MagicMock

# Añadir el directorio src al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

class TestDocumentTools(unittest.TestCase):
    """Pruebas para las herramientas de procesamiento de documentos."""
    
    def setUp(self):
        """Configuración inicial para cada prueba."""
        # Importar las funciones a probar
        from tools.document_tools import learn_text, learn_document, learn_from_url
        
        self.learn_text = learn_text
        self.learn_document = learn_document
        self.learn_from_url = learn_from_url
        
        # Configurar estado RAG simulado
        self.mock_rag_state = {
            "vector_store": Mock(),
            "initialized": True
        }
        
        # Configurar funciones de configuración
        from tools.document_tools import set_rag_state, set_md_converter, set_save_processed_copy_func
        
        set_rag_state(self.mock_rag_state)
        
        # Mock para conversor MarkItDown
        self.mock_md_converter = Mock()
        self.mock_md_converter.convert.return_value = "Contenido procesado de URL"
        set_md_converter(self.mock_md_converter)
        
        # Mock para función de guardar copia
        self.mock_save_func = Mock()
        self.mock_save_func.return_value = "copia_procesada.md"
        set_save_processed_copy_func(self.mock_save_func)
    
    def test_learn_text_basic(self):
        """Prueba básica de learn_text con texto válido."""
        text = "Este es un texto de prueba para el sistema RAG."
        source = "test_source"
        
        # Configurar mock para vector_store
        self.mock_rag_state["vector_store"].add_texts.return_value = ["doc_id_1"]
        
        result = self.learn_text(text, source)
        
        # Verificar que se llamó a add_texts
        self.mock_rag_state["vector_store"].add_texts.assert_called_once()
        
        # Verificar que el resultado contiene información de éxito
        self.assertIn("añadido", result.lower() or "procesado" in result.lower())
    
    def test_learn_text_empty_text(self):
        """Prueba learn_text con texto vacío."""
        result = self.learn_text("", "test_source")
        
        # Debería manejar texto vacío correctamente
        self.assertIsNotNone(result)
        self.assertIn("error", result.lower() or "vacío" in result.lower())
    
    def test_learn_text_no_rag_state(self):
        """Prueba learn_text sin estado RAG configurado."""
        from tools.document_tools import set_rag_state
        set_rag_state({})  # Estado vacío
        
        result = self.learn_text("Texto de prueba", "test_source")
        
        # Debería manejar estado RAG no inicializado
        self.assertIsNotNone(result)
        self.assertIn("error", result.lower() or "inicializado" in result.lower())
    
    def test_learn_document_valid_file(self):
        """Prueba learn_document con archivo válido."""
        # Crear archivo temporal
        test_content = """
# Documento de Prueba

Este es un documento de prueba para verificar el procesamiento.

## Sección 1
- Punto 1
- Punto 2

## Sección 2
Texto de ejemplo para procesamiento.
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(test_content)
            test_file = f.name
        
        try:
            # Configurar mock para vector_store
            self.mock_rag_state["vector_store"].add_texts.return_value = ["doc_id_1"]
            
            result = self.learn_document(test_file)
            
            # Verificar que se procesó el archivo
            self.assertIsNotNone(result)
            self.assertIn("procesado", result.lower() or "añadido" in result.lower())
            
            # Verificar que se llamó a la función de guardar copia
            self.mock_save_func.assert_called_once()
            
        finally:
            # Limpiar archivo temporal
            try:
                os.unlink(test_file)
            except:
                pass
    
    def test_learn_document_nonexistent_file(self):
        """Prueba learn_document con archivo inexistente."""
        result = self.learn_document("archivo_que_no_existe.txt")
        
        # Debería manejar archivo inexistente
        self.assertIsNotNone(result)
        self.assertIn("error", result.lower() or "no encontrado" in result.lower())
    
    def test_learn_from_url_valid(self):
        """Prueba learn_from_url con URL válida."""
        url = "https://httpbin.org/html"
        
        # Configurar mock para vector_store
        self.mock_rag_state["vector_store"].add_texts.return_value = ["doc_id_1"]
        
        result = self.learn_from_url(url)
        
        # Verificar que se procesó la URL
        self.assertIsNotNone(result)
        self.assertIn("procesada", result.lower() or "añadido" in result.lower())
        
        # Verificar que se llamó al conversor MarkItDown
        self.mock_md_converter.convert.assert_called_once_with(url)
        
        # Verificar que se llamó a la función de guardar copia
        self.mock_save_func.assert_called_once()
    
    def test_learn_from_url_invalid(self):
        """Prueba learn_from_url con URL inválida."""
        # Configurar mock para que falle
        self.mock_md_converter.convert.side_effect = Exception("Error de conexión")
        
        result = self.learn_from_url("https://url-invalida-12345.com")
        
        # Debería manejar URL inválida
        self.assertIsNotNone(result)
        self.assertIn("error", result.lower() or "no se pudo" in result.lower())
    
    def test_error_handling_vector_store_failure(self):
        """Prueba manejo de errores cuando falla el vector store."""
        # Configurar mock para que falle
        self.mock_rag_state["vector_store"].add_texts.side_effect = Exception("Error de base de datos")
        
        result = self.learn_text("Texto de prueba", "test_source")
        
        # Debería manejar error del vector store
        self.assertIsNotNone(result)
        self.assertIn("error", result.lower())

class TestDocumentToolsConfiguration(unittest.TestCase):
    """Pruebas para la configuración de las herramientas de documentos."""
    
    def test_set_rag_state(self):
        """Prueba la función set_rag_state."""
        from tools.document_tools import set_rag_state, rag_state
        
        test_state = {"test": "value", "initialized": True}
        set_rag_state(test_state)
        
        # Verificar que el estado se configuró correctamente
        self.assertEqual(rag_state, test_state)
    
    def test_set_md_converter(self):
        """Prueba la función set_md_converter."""
        from tools.document_tools import set_md_converter, md_converter
        
        mock_converter = Mock()
        set_md_converter(mock_converter)
        
        # Verificar que el conversor se configuró correctamente
        self.assertEqual(md_converter, mock_converter)
    
    def test_set_save_processed_copy_func(self):
        """Prueba la función set_save_processed_copy_func."""
        from tools.document_tools import set_save_processed_copy_func, save_processed_copy_func
        
        mock_func = Mock()
        set_save_processed_copy_func(mock_func)
        
        # Verificar que la función se configuró correctamente
        self.assertEqual(save_processed_copy_func, mock_func)

if __name__ == '__main__':
    unittest.main() 