#!/usr/bin/env python3
"""
Bulk Ingest GUI 导入测试脚本
用于验证所有关键模块的导入
"""

import sys
import os
from pathlib import Path

def test_imports():
    """测试所有必要的导入"""
    
    # 配置路径
    current_dir = Path(__file__).parent.resolve()
    project_root = current_dir.parent.resolve()
    mcp_src_dir = project_root / "mcp_server_organized" / "src"
    
    # 切换到 GUI 目录
    os.chdir(current_dir)
    
    # 配置 sys.path
    sys.path.insert(0, str(current_dir))
    sys.path.insert(0, str(project_root))
    if mcp_src_dir.exists():
        sys.path.insert(0, str(mcp_src_dir))
    
    print("🧪 正在测试模块导入...")
    
    # 测试 GUI 相关模块导入
    try:
        from services.configuration_service import ConfigurationService
        print("✅ 成功导入 ConfigurationService")
    except Exception as e:
        print(f"❌ 导入 ConfigurationService 时出错: {e}")
        return False
    
    try:
        from services.document_service import DocumentService
        print("✅ 成功导入 DocumentService")
    except Exception as e:
        print(f"❌ 导入 DocumentService 时出错: {e}")
        return False
    
    try:
        from controllers.main_controller import MainController
        print("✅ 成功导入 MainController")
    except Exception as e:
        print(f"❌ 导入 MainController 时出错: {e}")
        return False
    
    try:
        from views.main_view import MainView
        print("✅ 成功导入 MainView")
    except Exception as e:
        print(f"❌ 导入 MainView 时出错: {e}")
        return False
    
    try:
        from models.document_model import DocumentPreview
        print("✅ 成功导入 DocumentPreview")
    except Exception as e:
        print(f"❌ 导入 DocumentPreview 时出错: {e}")
        return False
    
    # 测试 RAG 核心模块导入
    try:
        from mcp_server_organized.src.rag_core import log
        print("✅ 成功从模块化结构导入 RAG 核心")
    except Exception as e:
        try:
            from rag_core import log
            print("✅ 成功从原始结构导入 RAG 核心")
        except Exception as e2:
            print(f"❌ 导入 RAG 核心时出错: {e2}")
            return False
    
    # 测试 Tkinter 导入
    try:
        import tkinter as tk
        print("✅ 成功导入 Tkinter")
    except Exception as e:
        print(f"❌ 导入 Tkinter 时出错: {e}")
        return False
    
    print("🎉 所有模块导入均正常！")
    return True

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)