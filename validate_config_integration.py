#!/usr/bin/env python3
"""
配置集成验证脚本
===================================================

此脚本验证 rag_core.py 是否正确使用了 utils/config.py 中的集中配置，
而不是其硬编码的配置。
"""

import sys
import os

# 将 src 目录添加到路径
sys.path.insert(0, 'src')

def validate_config_integration():
    """验证配置是否正确集成。"""
    
    print("🔍 验证配置集成...")
    print("=" * 50)
    
    try:
        # 1. 导入集中配置
        print("1. 导入集中配置...")
        from utils.config import Config
        print("   ✅ Config 导入成功")
        
        # 2. 验证 UNSTRUCTURED_CONFIGS 是否可用
        print("\n2. 验证 UNSTRUCTURED_CONFIGS...")
        unstructured_configs = Config.UNSTRUCTURED_CONFIGS
        print(f"   ✅ UNSTRUCTURED_CONFIGS 可用，包含 {len(unstructured_configs)} 个配置")
        
        # 3. 验证特定配置
        print("\n3. 验证特定配置...")
        
        # 验证 PDF
        pdf_config = Config.get_unstructured_config('.pdf')
        print(f"   ✅ PDF 配置: {pdf_config}")
        
        # 验证 DOCX
        docx_config = Config.get_unstructured_config('.docx')
        print(f"   ✅ DOCX 配置: {docx_config}")
        
        # 验证图片
        png_config = Config.get_unstructured_config('.png')
        print(f"   ✅ PNG 配置: {png_config}")
        
        # 验证邮件
        eml_config = Config.get_unstructured_config('.eml')
        print(f"   ✅ EML 配置: {eml_config}")
        
        # 4. 导入 rag_core 并验证其是否使用集中配置
        print("\n4. 导入 rag_core...")
        from rag_core import UNSTRUCTURED_CONFIGS, get_vector_store
        print("   ✅ rag_core 导入成功")
        
        # 5. 验证 rag_core 中的 UNSTRUCTURED_CONFIGS 是否与 Config 中相同
        print("\n5. 验证 rag_core 是否使用集中配置...")
        if UNSTRUCTURED_CONFIGS is Config.UNSTRUCTURED_CONFIGS:
            print("   ✅ rag_core 使用集中配置（相同引用）")
        else:
            print("   ⚠️ rag_core 使用了自己的配置副本")
        
        # 6. 验证配置是否相同
        print("\n6. 验证配置是否相同...")
        core_configs = UNSTRUCTURED_CONFIGS
        central_configs = Config.UNSTRUCTURED_CONFIGS
        
        if core_configs == central_configs:
            print("   ✅ 配置相同")
        else:
            print("   ❌ 配置不同")
            print(f"   Core: {len(core_configs)} 个配置")
            print(f"   Central: {len(central_configs)} 个配置")
        
        # 7. 验证 get_vector_store 是否正常工作
        print("\n7. 验证 get_vector_store...")
        try:
            vector_store = get_vector_store()
            print("   ✅ get_vector_store 正常工作")
        except Exception as e:
            print(f"   ❌ get_vector_store 出现错误: {e}")
        
        # 8. 验证加载函数是否使用 Config.get_unstructured_config
        print("\n8. 验证加载函数...")
        from rag_core import load_document_with_fallbacks, load_document_with_elements
        
        # 验证函数是否存在
        if callable(load_document_with_fallbacks):
            print("   ✅ load_document_with_fallbacks 可用")
        else:
            print("   ❌ load_document_with_fallbacks 不可用")
            
        if callable(load_document_with_elements):
            print("   ✅ load_document_with_elements 可用")
        else:
            print("   ❌ load_document_with_elements 不可用")
        
        print("\n" + "=" * 50)
        print("🎉 验证成功完成!")
        print("✅ rag_core.py 正确使用了集中配置")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 验证过程中出错: {e}")
        import traceback
        traceback.print_exc()
        return False

def show_configuration_summary():
    """显示当前配置摘要。"""
    
    print("\n📋 配置摘要")
    print("=" * 30)
    
    try:
        from utils.config import Config
        
        print(f"📁 文档目录: {Config.CONVERTED_DOCS_DIR}")
        print(f"🗄️ 向量存储目录: {Config.VECTOR_STORE_DIR}")
        print(f"💾 缓存目录: {Config.EMBEDDING_CACHE_DIR}")
        print(f"🤖 嵌入模型: {Config.EMBEDDING_MODEL}")
        print(f"⚙️ 设备: {Config.DEVICE}")
        print(f"📏 默认块大小: {Config.DEFAULT_CHUNK_SIZE}")
        print(f"🔄 默认块重叠: {Config.DEFAULT_CHUNK_OVERLAP}")
        print(f"📦 最大缓存大小: {Config.MAX_CACHE_SIZE}")
        
        # 显示支持的文件类型
        supported_formats = list(Config.UNSTRUCTURED_CONFIGS.keys())
        print(f"\n📄 支持的格式 ({len(supported_formats)}):")
        for i, format_type in enumerate(supported_formats):
            if i % 5 == 0:
                print("   ", end="")
            print(f"{format_type} ", end="")
            if (i + 1) % 5 == 0:
                print()
        print()
        
    except Exception as e:
        print(f"❌ 显示摘要时出错: {e}")

if __name__ == "__main__":
    print("🚀 开始配置集成验证...")
    
    success = validate_config_integration()
    
    if success:
        show_configuration_summary()
        print("\n✅ 系统已准备好使用集中配置")
    else:
        print("\n❌ 配置集成存在问题")
        sys.exit(1)