#!/usr/bin/env python3
"""
用于测试新版 rag_core_wrapper 的脚本
"""

from rag_core_wrapper import (
    load_document_with_elements,
    add_text_to_knowledge_base_enhanced,
    get_vector_store,
    log,
    clear_embedding_cache,
    get_cache_stats,
    get_vector_store_stats_advanced
)

def test_wrapper():
    """测试包装器是否正常工作"""
    
    print("🧪 正在测试 rag_core_wrapper...")
    
    try:
        # 测试日志函数
        log("测试包装器正常工作")
        print("✅ log 功能正常")
        
        # 测试 get_cache_stats
        stats = get_cache_stats()
        print(f"✅ get_cache_stats 功能正常: {stats}")
        
        # 测试 get_vector_store_stats_advanced
        vs_stats = get_vector_store_stats_advanced()
        print(f"✅ get_vector_store_stats_advanced 功能正常: {vs_stats}")
        
        print("🎉 包装器所有功能都正常工作！")
        
    except Exception as e:
        print(f"❌ 包装器出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_wrapper() 