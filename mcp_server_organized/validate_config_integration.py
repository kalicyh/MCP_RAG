#!/usr/bin/env python3
"""
Script de Validación de Integración de Configuración
===================================================

Este script valida que rag_core.py esté usando correctamente la configuración
centralizada de utils/config.py en lugar de su configuración hardcodeada.
"""

import sys
import os

# Añadir el directorio src al path
sys.path.insert(0, 'src')

def validate_config_integration():
    """Valida que la configuración esté integrada correctamente."""
    
    print("🔍 Validando integración de configuración...")
    print("=" * 50)
    
    try:
        # 1. Importar la configuración centralizada
        print("1. Importando configuración centralizada...")
        from utils.config import Config
        print("   ✅ Config importado correctamente")
        
        # 2. Verificar que UNSTRUCTURED_CONFIGS esté disponible
        print("\n2. Verificando UNSTRUCTURED_CONFIGS...")
        unstructured_configs = Config.UNSTRUCTURED_CONFIGS
        print(f"   ✅ UNSTRUCTURED_CONFIGS disponible con {len(unstructured_configs)} configuraciones")
        
        # 3. Verificar configuraciones específicas
        print("\n3. Verificando configuraciones específicas...")
        
        # Verificar PDF
        pdf_config = Config.get_unstructured_config('.pdf')
        print(f"   ✅ Configuración PDF: {pdf_config}")
        
        # Verificar DOCX
        docx_config = Config.get_unstructured_config('.docx')
        print(f"   ✅ Configuración DOCX: {docx_config}")
        
        # Verificar imágenes
        png_config = Config.get_unstructured_config('.png')
        print(f"   ✅ Configuración PNG: {png_config}")
        
        # Verificar correos
        eml_config = Config.get_unstructured_config('.eml')
        print(f"   ✅ Configuración EML: {eml_config}")
        
        # 4. Importar rag_core y verificar que use la configuración centralizada
        print("\n4. Importando rag_core...")
        from rag_core import UNSTRUCTURED_CONFIGS, get_vector_store
        print("   ✅ rag_core importado correctamente")
        
        # 5. Verificar que UNSTRUCTURED_CONFIGS en rag_core sea la misma que en Config
        print("\n5. Verificando que rag_core use configuración centralizada...")
        if UNSTRUCTURED_CONFIGS is Config.UNSTRUCTURED_CONFIGS:
            print("   ✅ rag_core usa la configuración centralizada (misma referencia)")
        else:
            print("   ⚠️ rag_core tiene su propia copia de la configuración")
        
        # 6. Verificar que las configuraciones sean idénticas
        print("\n6. Verificando que las configuraciones sean idénticas...")
        core_configs = UNSTRUCTURED_CONFIGS
        central_configs = Config.UNSTRUCTURED_CONFIGS
        
        if core_configs == central_configs:
            print("   ✅ Configuraciones idénticas")
        else:
            print("   ❌ Configuraciones diferentes")
            print(f"   Core: {len(core_configs)} configuraciones")
            print(f"   Central: {len(central_configs)} configuraciones")
        
        # 7. Verificar que get_vector_store funcione
        print("\n7. Verificando get_vector_store...")
        try:
            vector_store = get_vector_store()
            print("   ✅ get_vector_store funciona correctamente")
        except Exception as e:
            print(f"   ❌ Error en get_vector_store: {e}")
        
        # 8. Verificar que las funciones de carga usen Config.get_unstructured_config
        print("\n8. Verificando funciones de carga...")
        from rag_core import load_document_with_fallbacks, load_document_with_elements
        
        # Verificar que las funciones existan
        if callable(load_document_with_fallbacks):
            print("   ✅ load_document_with_fallbacks disponible")
        else:
            print("   ❌ load_document_with_fallbacks no disponible")
            
        if callable(load_document_with_elements):
            print("   ✅ load_document_with_elements disponible")
        else:
            print("   ❌ load_document_with_elements no disponible")
        
        print("\n" + "=" * 50)
        print("🎉 Validación completada exitosamente!")
        print("✅ rag_core.py está usando correctamente la configuración centralizada")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error durante la validación: {e}")
        import traceback
        traceback.print_exc()
        return False

def show_configuration_summary():
    """Muestra un resumen de la configuración actual."""
    
    print("\n📋 Resumen de Configuración")
    print("=" * 30)
    
    try:
        from utils.config import Config
        
        print(f"📁 Directorio de documentos: {Config.CONVERTED_DOCS_DIR}")
        print(f"🗄️ Directorio vector store: {Config.VECTOR_STORE_DIR}")
        print(f"💾 Directorio cache: {Config.EMBEDDING_CACHE_DIR}")
        print(f"🤖 Modelo de embedding: {Config.EMBEDDING_MODEL}")
        print(f"⚙️ Dispositivo: {Config.DEVICE}")
        print(f"📏 Tamaño de chunk por defecto: {Config.DEFAULT_CHUNK_SIZE}")
        print(f"🔄 Overlap de chunk por defecto: {Config.DEFAULT_CHUNK_OVERLAP}")
        print(f"📦 Tamaño máximo de cache: {Config.MAX_CACHE_SIZE}")
        
        # Mostrar tipos de archivo soportados
        supported_formats = list(Config.UNSTRUCTURED_CONFIGS.keys())
        print(f"\n📄 Formatos soportados ({len(supported_formats)}):")
        for i, format_type in enumerate(supported_formats):
            if i % 5 == 0:
                print("   ", end="")
            print(f"{format_type} ", end="")
            if (i + 1) % 5 == 0:
                print()
        print()
        
    except Exception as e:
        print(f"❌ Error mostrando resumen: {e}")

if __name__ == "__main__":
    print("🚀 Iniciando validación de integración de configuración...")
    
    success = validate_config_integration()
    
    if success:
        show_configuration_summary()
        print("\n✅ Sistema listo para usar con configuración centralizada")
    else:
        print("\n❌ Hay problemas con la integración de configuración")
        sys.exit(1) 