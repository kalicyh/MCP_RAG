#!/usr/bin/env python3
"""
Pruebas unitarias para las herramientas de utilidad.
Prueba las funciones de mantenimiento y estadísticas del sistema.
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# Añadir el directorio src al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

class TestUtilityTools(unittest.TestCase):
    """Pruebas para las herramientas de utilidad."""
    
    def setUp(self):
        """Configuración inicial para cada prueba."""
        # Importar las funciones a probar
        from tools.utility_tools import (
            get_knowledge_base_stats, get_embedding_cache_stats,
            clear_embedding_cache_tool, optimize_vector_database,
            get_vector_database_stats, reindex_vector_database
        )
        
        self.get_knowledge_base_stats = get_knowledge_base_stats
        self.get_embedding_cache_stats = get_embedding_cache_stats
        self.clear_embedding_cache_tool = clear_embedding_cache_tool
        self.optimize_vector_database = optimize_vector_database
        self.get_vector_database_stats = get_vector_database_stats
        self.reindex_vector_database = reindex_vector_database
        
        # Configurar estado RAG simulado
        self.mock_rag_state = {
            "vector_store": Mock(),
            "initialized": True
        }
        
        # Configurar vector store mock
        self.mock_vector_store = Mock()
        self.mock_vector_store.get.return_value = {
            "documents": ["doc1", "doc2", "doc3"],
            "total_count": 3,
            "metadata": {"sources": ["source1.txt", "source2.txt"]}
        }
        
        self.mock_rag_state["vector_store"] = self.mock_vector_store
        
        # Configurar estado
        from tools.utility_tools import set_rag_state
        set_rag_state(self.mock_rag_state)
    
    def test_get_knowledge_base_stats_basic(self):
        """Prueba básica de get_knowledge_base_stats."""
        result = self.get_knowledge_base_stats()
        
        # Verificar que se llamó al vector store
        self.mock_vector_store.get.assert_called_once()
        
        # Verificar que el resultado contiene estadísticas
        self.assertIsNotNone(result)
        self.assertIn("estadísticas", result.lower() or "stats" in result.lower())
    
    def test_get_knowledge_base_stats_no_rag_state(self):
        """Prueba get_knowledge_base_stats sin estado RAG configurado."""
        from tools.utility_tools import set_rag_state
        set_rag_state({})  # Estado vacío
        
        result = self.get_knowledge_base_stats()
        
        # Debería manejar estado RAG no inicializado
        self.assertIsNotNone(result)
        self.assertIn("error", result.lower() or "inicializado" in result.lower())
    
    def test_get_knowledge_base_stats_vector_store_failure(self):
        """Prueba get_knowledge_base_stats cuando falla el vector store."""
        # Configurar mock para que falle
        self.mock_vector_store.get.side_effect = Exception("Error de base de datos")
        
        result = self.get_knowledge_base_stats()
        
        # Debería manejar error del vector store
        self.assertIsNotNone(result)
        self.assertIn("error", result.lower())
    
    def test_get_embedding_cache_stats_basic(self):
        """Prueba básica de get_embedding_cache_stats."""
        result = self.get_embedding_cache_stats()
        
        # Verificar que el resultado contiene estadísticas del cache
        self.assertIsNotNone(result)
        self.assertIn("cache", result.lower() or "estadísticas" in result.lower())
    
    def test_clear_embedding_cache_tool_basic(self):
        """Prueba básica de clear_embedding_cache_tool."""
        result = self.clear_embedding_cache_tool()
        
        # Verificar que el resultado indica limpieza exitosa
        self.assertIsNotNone(result)
        self.assertIn("limpiado", result.lower() or "cache" in result.lower())
    
    def test_optimize_vector_database_basic(self):
        """Prueba básica de optimize_vector_database."""
        result = self.optimize_vector_database()
        
        # Verificar que el resultado indica optimización exitosa
        self.assertIsNotNone(result)
        self.assertIn("optimizada", result.lower() or "optimización" in result.lower())
    
    def test_get_vector_database_stats_basic(self):
        """Prueba básica de get_vector_database_stats."""
        result = self.get_vector_database_stats()
        
        # Verificar que el resultado contiene estadísticas de la BD
        self.assertIsNotNone(result)
        self.assertIn("estadísticas", result.lower() or "stats" in result.lower())
    
    def test_reindex_vector_database_basic(self):
        """Prueba básica de reindex_vector_database."""
        result = self.reindex_vector_database(profile="auto")
        
        # Verificar que el resultado indica reindexado exitoso
        self.assertIsNotNone(result)
        self.assertIn("reindexado", result.lower() or "reindex" in result.lower())
    
    def test_reindex_vector_database_custom_profile(self):
        """Prueba reindex_vector_database con perfil personalizado."""
        result = self.reindex_vector_database(profile="large")
        
        # Verificar que el resultado indica reindexado exitoso
        self.assertIsNotNone(result)
        self.assertIn("reindexado", result.lower() or "reindex" in result.lower())
    
    def test_error_handling_optimization_failure(self):
        """Prueba manejo de errores cuando falla la optimización."""
        # Simular fallo en optimización
        with patch('tools.utility_tools.optimize_vector_store') as mock_optimize:
            mock_optimize.side_effect = Exception("Error de optimización")
            
            result = self.optimize_vector_database()
            
            # Debería manejar error de optimización
            self.assertIsNotNone(result)
            self.assertIn("error", result.lower())
    
    def test_error_handling_reindex_failure(self):
        """Prueba manejo de errores cuando falla el reindexado."""
        # Simular fallo en reindexado
        with patch('tools.utility_tools.reindex_vector_store') as mock_reindex:
            mock_reindex.side_effect = Exception("Error de reindexado")
            
            result = self.reindex_vector_database(profile="auto")
            
            # Debería manejar error de reindexado
            self.assertIsNotNone(result)
            self.assertIn("error", result.lower())

class TestUtilityToolsConfiguration(unittest.TestCase):
    """Pruebas para la configuración de las herramientas de utilidad."""
    
    def test_set_rag_state(self):
        """Prueba la función set_rag_state."""
        from tools.utility_tools import set_rag_state, rag_state
        
        test_state = {"test": "value", "initialized": True}
        set_rag_state(test_state)
        
        # Verificar que el estado se configuró correctamente
        self.assertEqual(rag_state, test_state)
    
    def test_rag_state_persistence(self):
        """Prueba que el estado RAG persiste entre llamadas."""
        from tools.utility_tools import set_rag_state, rag_state
        
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

class TestUtilityToolsIntegration(unittest.TestCase):
    """Pruebas de integración para las herramientas de utilidad."""
    
    def test_cache_statistics_integration(self):
        """Prueba integración de estadísticas del cache."""
        from tools.utility_tools import get_embedding_cache_stats, clear_embedding_cache_tool
        
        # Obtener estadísticas iniciales
        initial_stats = get_embedding_cache_stats()
        self.assertIsNotNone(initial_stats)
        
        # Limpiar cache
        clear_result = clear_embedding_cache_tool()
        self.assertIsNotNone(clear_result)
        self.assertIn("limpiado", clear_result.lower())
        
        # Obtener estadísticas después de limpiar
        final_stats = get_embedding_cache_stats()
        self.assertIsNotNone(final_stats)
    
    def test_database_optimization_workflow(self):
        """Prueba flujo de trabajo de optimización de base de datos."""
        from tools.utility_tools import (
            get_vector_database_stats, 
            optimize_vector_database, 
            reindex_vector_database
        )
        
        # Obtener estadísticas iniciales
        initial_stats = get_vector_database_stats()
        self.assertIsNotNone(initial_stats)
        
        # Optimizar base de datos
        optimize_result = optimize_vector_database()
        self.assertIsNotNone(optimize_result)
        self.assertIn("optimizada", optimize_result.lower())
        
        # Reindexar base de datos
        reindex_result = reindex_vector_database(profile="auto")
        self.assertIsNotNone(reindex_result)
        self.assertIn("reindexado", reindex_result.lower())
        
        # Obtener estadísticas finales
        final_stats = get_vector_database_stats()
        self.assertIsNotNone(final_stats)
    
    def test_comprehensive_system_maintenance(self):
        """Prueba mantenimiento completo del sistema."""
        from tools.utility_tools import (
            get_knowledge_base_stats,
            get_embedding_cache_stats,
            clear_embedding_cache_tool,
            optimize_vector_database,
            get_vector_database_stats,
            reindex_vector_database
        )
        
        # 1. Obtener estadísticas iniciales
        kb_stats = get_knowledge_base_stats()
        cache_stats = get_embedding_cache_stats()
        db_stats = get_vector_database_stats()
        
        self.assertIsNotNone(kb_stats)
        self.assertIsNotNone(cache_stats)
        self.assertIsNotNone(db_stats)
        
        # 2. Realizar mantenimiento
        clear_result = clear_embedding_cache_tool()
        optimize_result = optimize_vector_database()
        reindex_result = reindex_vector_database(profile="auto")
        
        self.assertIsNotNone(clear_result)
        self.assertIsNotNone(optimize_result)
        self.assertIsNotNone(reindex_result)
        
        # 3. Verificar que todas las operaciones fueron exitosas
        self.assertIn("limpiado", clear_result.lower())
        self.assertIn("optimizada", optimize_result.lower())
        self.assertIn("reindexado", reindex_result.lower())

class TestUtilityToolsEdgeCases(unittest.TestCase):
    """Pruebas de casos edge para las herramientas de utilidad."""
    
    def test_empty_vector_store_stats(self):
        """Prueba estadísticas con vector store vacío."""
        from tools.utility_tools import get_knowledge_base_stats, set_rag_state
        
        # Configurar vector store vacío
        empty_vector_store = Mock()
        empty_vector_store.get.return_value = {
            "documents": [],
            "total_count": 0,
            "metadata": {}
        }
        
        empty_state = {"vector_store": empty_vector_store, "initialized": True}
        set_rag_state(empty_state)
        
        result = get_knowledge_base_stats()
        
        # Debería manejar vector store vacío
        self.assertIsNotNone(result)
        self.assertIn("0", result or "vacía" in result.lower())
    
    def test_large_vector_store_stats(self):
        """Prueba estadísticas con vector store grande."""
        from tools.utility_tools import get_knowledge_base_stats, set_rag_state
        
        # Configurar vector store grande
        large_vector_store = Mock()
        large_vector_store.get.return_value = {
            "documents": ["doc" + str(i) for i in range(1000)],
            "total_count": 1000,
            "metadata": {"sources": ["source" + str(i) + ".txt" for i in range(100)]}
        }
        
        large_state = {"vector_store": large_vector_store, "initialized": True}
        set_rag_state(large_state)
        
        result = get_knowledge_base_stats()
        
        # Debería manejar vector store grande
        self.assertIsNotNone(result)
        self.assertIn("1000", result or "grande" in result.lower())
    
    def test_invalid_profile_reindex(self):
        """Prueba reindexado con perfil inválido."""
        from tools.utility_tools import reindex_vector_database
        
        result = reindex_vector_database(profile="invalid_profile")
        
        # Debería manejar perfil inválido
        self.assertIsNotNone(result)
        # Puede devolver error o usar perfil por defecto
        self.assertTrue(len(result) > 0)

if __name__ == '__main__':
    unittest.main() 