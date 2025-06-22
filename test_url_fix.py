#!/usr/bin/env python3
"""
Script de prueba para verificar las mejoras en el procesamiento de URLs con PDFs.
Incluye timeout específico y logs detallados para diagnosticar problemas.
"""

import time
import sys
import os
import threading
from datetime import datetime

# Agregar el directorio actual al path para importar los módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_pdf_timeout():
    """Prueba específica para el timeout de PDFs con logs detallados."""
    print("🔍 **PRUEBA DE TIMEOUT PARA PDFs**")
    print("=" * 50)
    
    # URL de prueba (PDF real)
    test_url = "https://iestpcabana.edu.pe/wp-content/uploads/2021/09/Programacion-con-PHP.pdf"
    
    print(f"📄 **URL de prueba:** {test_url}")
    print(f"⏰ **Inicio:** {datetime.now().strftime('%H:%M:%S')}")
    
    try:
        # Importar el módulo del servidor
        from rag_server import learn_from_url
        
        print("✅ **Módulo importado correctamente**")
        
        # Ejecutar la función con timeout
        start_time = time.time()
        
        print("🚀 **Iniciando procesamiento...**")
        result = learn_from_url(test_url)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        print(f"⏱️ **Tiempo total:** {processing_time:.2f} segundos")
        print(f"📊 **Resultado:**")
        print("-" * 30)
        print(result)
        print("-" * 30)
        
        if processing_time > 120:
            print("⚠️ **ADVERTENCIA:** El procesamiento tardó más de 2 minutos")
        else:
            print("✅ **ÉXITO:** Procesamiento completado dentro del tiempo esperado")
            
    except Exception as e:
        print(f"❌ **ERROR:** {e}")
        import traceback
        traceback.print_exc()

def test_pdf_fallback():
    """Prueba el fallback con PyPDF2 para PDFs problemáticos."""
    print("\n🔧 **PRUEBA DE FALLBACK PyPDF2**")
    print("=" * 50)
    
    try:
        import PyPDF2
        print("✅ **PyPDF2 disponible**")
        
        # Crear un PDF de prueba simple
        test_pdf_path = "test_simple.pdf"
        
        # Intentar crear un PDF simple para prueba
        try:
            from reportlab.pdfgen import canvas
            c = canvas.Canvas(test_pdf_path)
            c.drawString(100, 750, "Este es un PDF de prueba simple")
            c.drawString(100, 700, "Para verificar el fallback de PyPDF2")
            c.save()
            print(f"✅ **PDF de prueba creado:** {test_pdf_path}")
            
            # Probar PyPDF2
            with open(test_pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page_num, page in enumerate(pdf_reader.pages):
                    page_text = page.extract_text()
                    if page_text:
                        text += f"\n--- Página {page_num + 1} ---\n{page_text}\n"
                
                print(f"✅ **PyPDF2 funcionando:** {len(text)} caracteres extraídos")
                print(f"📄 **Contenido:** {text[:100]}...")
            
            # Limpiar
            os.remove(test_pdf_path)
            
        except ImportError:
            print("⚠️ **reportlab no disponible, saltando creación de PDF de prueba**")
            
    except ImportError:
        print("❌ **PyPDF2 no disponible**")
        print("💡 **Instalar:** pip install PyPDF2")

def test_unstructured_timeout():
    """Prueba específica del timeout de Unstructured."""
    print("\n⏱️ **PRUEBA DE TIMEOUT DE UNSTRUCTURED**")
    print("=" * 50)
    
    try:
        from unstructured.partition.auto import partition
        
        # Crear un archivo de texto simple para prueba
        test_file = "test_timeout.txt"
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write("Este es un archivo de prueba simple para verificar el timeout de Unstructured.\n" * 100)
        
        print(f"📄 **Archivo de prueba creado:** {test_file}")
        
        # Probar con timeout
        def process_with_timeout():
            try:
                elements = partition(filename=test_file, strategy="fast", max_partition=1000)
                return elements
            except Exception as e:
                return f"Error: {e}"
        
        # Ejecutar con timeout
        thread = threading.Thread(target=lambda: setattr(process_with_timeout, 'result', process_with_timeout()))
        thread.daemon = True
        thread.start()
        
        start_time = time.time()
        thread.join(timeout=30)  # 30 segundos de timeout
        end_time = time.time()
        
        if thread.is_alive():
            print("❌ **TIMEOUT:** Unstructured tardó más de 30 segundos")
        else:
            print(f"✅ **ÉXITO:** Unstructured completado en {end_time - start_time:.2f} segundos")
        
        # Limpiar
        os.remove(test_file)
        
    except Exception as e:
        print(f"❌ **ERROR:** {e}")

def main():
    """Función principal que ejecuta todas las pruebas."""
    print("🧪 **SUITE DE PRUEBAS PARA MEJORAS DE URL**")
    print("=" * 60)
    print(f"🕐 **Inicio:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Ejecutar pruebas
    test_pdf_fallback()
    test_unstructured_timeout()
    test_pdf_timeout()
    
    print("\n" + "=" * 60)
    print(f"🏁 **Fin de pruebas:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n💡 **Recomendaciones:**")
    print("- Si hay timeouts, considera usar PDFs más pequeños")
    print("- Verifica que PyPDF2 esté instalado para fallbacks")
    print("- Monitorea el uso de memoria durante el procesamiento")

if __name__ == "__main__":
    main() 