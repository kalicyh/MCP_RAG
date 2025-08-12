
#!/usr/bin/env python3
"""
Bulk Ingest GUI 启动脚本
可在任意位置运行应用
适配 MCP 服务器新模块化结构
"""

import sys
import os
from pathlib import Path


# 配置 sys.path 以支持绝对导入
current_dir = Path(__file__).parent.resolve()
project_root = current_dir.parent.resolve()

# 切换到 GUI 目录，确保相对导入可用
os.chdir(current_dir)

# 将目录添加到 path
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(project_root))

# MCP 服务器路径配置（需在任何导入前设置）
mcp_src_dir = project_root / "mcp_server_organized" / "src"
if mcp_src_dir.exists():
    sys.path.insert(0, str(mcp_src_dir))
    print(f"✅ MCP 服务器路径已配置: {mcp_src_dir}")

# 检查 RAG 核心是否在新结构中
rag_core_found = False
rag_core_path = None

# 在新模块化结构中查找
modular_rag_core = project_root / "mcp_server_organized" / "src" / "rag_core.py"
if modular_rag_core.exists():
    rag_core_found = True
    rag_core_path = modular_rag_core
    print(f"✅ RAG 核心已在模块化结构中找到: {rag_core_path}")
else:
    # 备用：查找原始结构
    original_rag_core = project_root / "rag_core.py"
    if original_rag_core.exists():
        rag_core_found = True
        rag_core_path = original_rag_core
        print(f"⚠️ RAG 核心在原始结构中找到: {rag_core_path}")
    else:
        print("❌ 错误：未找到 RAG 核心")
        print(f"查找路径:")
        print(f"  - 模块化结构: {modular_rag_core}")
        print(f"  - 原始结构: {original_rag_core}")
        sys.exit(1)

def main():
    """主启动函数"""
    try:
        print("🚀 正在启动 Bulk Ingest GUI...")
        print(f"📁 当前目录: {os.getcwd()}")
        print(f"📁 项目根目录: {project_root}")
        print(f"🔍 RAG 核心路径: {rag_core_path}")

        # 逐步导入并运行主程序，便于定位问题
        print("📦 正在导入模块...")
        print("  - 导入 main...")
        import main

        print("  - 执行 main.main()...")
        main.main()

    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("请确保所有依赖已安装:")
        print("pip install -r requirements.txt")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    except Exception as e:
        print(f"💥 应用运行出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main() 