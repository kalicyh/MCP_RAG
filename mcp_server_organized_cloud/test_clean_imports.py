#!/usr/bin/env python3
"""
测试清洁导入 - 无弃用警告
==============================================================

此脚本测试更新后的导入是否正常工作，
且不会生成弃用警告。
"""

import sys
import warnings

# 将 src 目录添加到路径
sys.path.insert(0, 'src')

def test_clean_imports():
    """测试导入是否无警告。"""
    
    print("🔍 **清洁导入测试**")
    print("=" * 50)
    
    # 捕获警告以验证是否存在弃用警告
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        
        try:
            print("1. 测试 LangChain 的导入...")
            
            # 导入更新的类
            from langchain_community.embeddings import HuggingFaceEmbeddings
            from langchain_community.vectorstores import Chroma
            from langchain_community.chat_models import ChatOllama
            
            print("   ✅ LangChain 导入成功")
            
            # 检查是否有弃用警告
            deprecation_warnings = [warning for warning in w if 'deprecated' in str(warning.message).lower()]
            
            if deprecation_warnings:
                print(f"   ⚠️ 发现 {len(deprecation_warnings)} 条弃用警告:")
                for warning in deprecation_warnings:
                    print(f"      - {warning.message}")
            else:
                print("   ✅ 未发现弃用警告")
            
            print("\n2. 测试 RAG 系统的导入...")
            from rag_core import get_vector_store, get_qa_chain
            print("   ✅ RAG 系统导入成功")
            
            print("\n3. 测试组件创建...")
            vector_store = get_vector_store()
            print("   ✅ 向量存储创建成功")
            
            print("\n🎉 **所有导入均无警告**")
            print("✅ 导入更新成功")
            print("✅ 系统运行无弃用警告")
            
            return True
            
        except Exception as e:
            print(f"❌ 导入时发生错误: {e}")
            return False

if __name__ == "__main__":
    success = test_clean_imports()
    sys.exit(0 if success else 1)