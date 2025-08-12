#!/usr/bin/env python3
"""
用于验证 rag_core 包装器功能的测试脚本
"""

import sys
import os
from pathlib import Path

def test_rag_core_wrapper():
    """测试 rag_core 包装器"""
    
    # 配置路径
    current_dir = Path(__file__).parent.resolve()
    project_root = current_dir.parent.resolve()
    
    # 切换到 GUI 目录
    os.chdir(current_dir)
    
    # 配置 sys.path
    sys.path.insert(0, str(current_dir))
    sys.path.insert(0, str(project_root))
    
    print("🧪 正在测试 rag_core 包装器...")
    
    try:
        # Importar el wrapper
        from rag_core_wrapper import (
            load_document_with_elements,
            add_text_to_knowledge_base_enhanced,
            get_vector_store,
            log,
            clear_embedding_cache,
            get_cache_stats,
            get_vector_store_stats_advanced
        )
        
        print("✅ 成功导入包装器")
        
        # Probar una función simple
        try:
            log("测试 rag_core 包装器的 log 功能")
            print("✅ log 功能正常")
        except Exception as e:
            print(f"⚠️ Función log no funciona: {e}")
        
        # Probar obtener estadísticas del cache
        try:
            stats = get_cache_stats()
            print("✅ get_cache_stats 功能正常")
            print(f"   统计信息: {stats}")
        except Exception as e:
            print(f"⚠️ get_cache_stats 功能异常: {e}")
        
        return True
        
    except ImportError as e:
        print(f"❌ 导入包装器错误: {e}")
        return False
    except Exception as e:
        print(f"❌ 测试包装器错误: {e}")
        return False

if __name__ == "__main__":
    success = test_rag_core_wrapper()
    sys.exit(0 if success else 1) 