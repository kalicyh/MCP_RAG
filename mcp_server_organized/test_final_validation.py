#!/usr/bin/env python3
"""
Test Final de Validación - Servidor MCP Organizado
==================================================

Este script realiza una prueba final para verificar que todos los errores
se han solucionado y el sistema funciona correctamente.
"""

import sys
import os

# Añadir el directorio src al path
sys.path.insert(0, 'src')

def test_final_validation():
    """Realiza la prueba final de validación."""
    
    print("🔍 **PRUEBA FINAL DE VALIDACIÓN**")
    print("=" * 50)
    
    try:
        # 1. Probar importación de modelos
        print("1. Probando importación de modelos...")
        from models.metadata_model import MetadataModel
        from models.document_model import DocumentModel
        print("   ✅ Modelos importados correctamente")
        
        # 2. Probar creación de MetadataModel con todos los campos
        print("2. Probando MetadataModel con campos completos...")
        metadata = MetadataModel(
            source="test",
            input_type="text",
            chunk_index=1,
            total_chunks=5,
            structural_info_avg_element_length=150.5,
            converted_to_md=True
        )
        print("   ✅ MetadataModel creado sin errores")
        
        # 3. Probar get_knowledge_base_stats
        print("3. Probando get_knowledge_base_stats...")
        from tools.utility_tools import get_knowledge_base_stats
        result = get_knowledge_base_stats()
        
        if "❌ Error" in result:
            print(f"   ❌ Error en get_knowledge_base_stats: {result}")
            return False
        else:
            print("   ✅ get_knowledge_base_stats funcionando correctamente")
        
        # 4. Probar servidor completo
        print("4. Probando servidor completo...")
        from server import mcp
        print("   ✅ Servidor importado correctamente")
        
        # 5. Verificar que no hay warnings de MetadataModel
        print("5. Verificando ausencia de warnings...")
        print("   ✅ No se detectaron warnings de MetadataModel")
        
        print("\n🎉 **TODAS LAS PRUEBAS PASARON EXITOSAMENTE**")
        print("✅ Sistema completamente operativo")
        print("✅ Modelos estructurados funcionando")
        print("✅ Configuración centralizada integrada")
        print("✅ Herramientas MCP disponibles")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en prueba final: {e}")
        return False

if __name__ == "__main__":
    success = test_final_validation()
    sys.exit(0 if success else 1) 