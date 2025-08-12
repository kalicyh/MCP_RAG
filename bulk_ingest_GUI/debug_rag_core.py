#!/usr/bin/env python3
"""
rag_core 诊断脚本
"""

import sys
import os
from pathlib import Path

def debug_rag_core():
    """诊断 rag_core 问题"""
    
    print("🔍 诊断 rag_core...")
    
    # 配置路径
    current_dir = Path(__file__).parent.resolve()
    project_root = current_dir.parent.resolve()
    mcp_src_dir = project_root / "mcp_server_organized" / "src"
    
    print(f"📁 当前目录: {current_dir}")
    print(f"📁 项目目录: {project_root}")
    print(f"📁 MCP src 目录: {mcp_src_dir}")
    print(f"📁 MCP src 存在: {mcp_src_dir.exists()}")
    
    # 验证文件
    rag_core_path = mcp_src_dir / "rag_core.py"
    utils_config_path = mcp_src_dir / "utils" / "config.py"
    
    print(f"📄 rag_core.py 存在: {rag_core_path.exists()}")
    print(f"📄 utils/config.py 存在: {utils_config_path.exists()}")
    
    # 配置路径
    if mcp_src_dir.exists():
        sys.path.insert(0, str(mcp_src_dir))
        print(f"✅ 路径已配置: {mcp_src_dir}")
    
    # 测试 utils.config 导入
    try:
        # 从 MCP 服务器直接导入
        import utils.config
        print("✅ utils.config 导入成功")
    except ImportError as e:
        print(f"❌ 导入 utils.config 错误: {e}")
    
    # 测试 rag_core 导入
    try:
        import rag_core
        print("✅ 成功导入 rag_core")

        # 测试特定函数
        try:
            from rag_core import load_document_with_elements
            print("✅ 成功导入 load_document_with_elements")
        except ImportError as e:
            print(f"❌ 导入 load_document_with_elements 错误: {e}")
        
        try:
            from rag_core import log
            print("✅ 成功导入 log")
            log("诊断测试")
        except ImportError as e:
            print(f"❌ 导入 log 错误: {e}")
        
    except ImportError as e:
        print(f"❌ 导入 rag_core 错误: {e}")
        print(f"   sys.path: {sys.path[:5]}...")  # 仅显示前 5 个元素

if __name__ == "__main__":
    debug_rag_core() 