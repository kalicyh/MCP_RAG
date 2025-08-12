#!/usr/bin/env python3
"""
批量导入 GUI 的替代启动脚本
可从任何位置工作
为 MCP 服务器的新模块化结构配置
"""

import sys
import os
from pathlib import Path

def setup_environment():
    """配置应用程序环境"""
    # 获取当前脚本路径
    script_path = Path(__file__).resolve()
    gui_dir = script_path.parent
    project_root = gui_dir.parent
    
    # 切换到 GUI 目录以便相对导入正常工作
    os.chdir(gui_dir)
    
    # 将目录添加到路径
    sys.path.insert(0, str(gui_dir))
    sys.path.insert(0, str(project_root))
    
    # 验证新结构中 RAG 核心是否可用
    rag_core_found = False
    rag_core_path = None
    
    # 在新的模块化结构中搜索
    modular_rag_core = project_root / "mcp_server_organized" / "src" / "rag_core.py"
    if modular_rag_core.exists():
        rag_core_found = True
        rag_core_path = modular_rag_core
        print(f"✅ 在模块化结构中找到 RAG 核心: {rag_core_path}")
    else:
        # 回退：在原始结构中搜索
        original_rag_core = project_root / "rag_core.py"
        if original_rag_core.exists():
            rag_core_found = True
            rag_core_path = original_rag_core
            print(f"⚠️ 在原始结构中找到 RAG 核心: {rag_core_path}")
        else:
            print(f"❌ 错误：未找到 RAG 核心")
            print(f"搜索位置:")
            print(f"  - 模块化结构: {modular_rag_core}")
            print(f"  - 原始结构: {original_rag_core}")
            return False
    
    print(f"✅ 环境已配置:")
    print(f"   📁 GUI 目录: {gui_dir}")
    print(f"   📁 项目根目录: {project_root}")
    print(f"   🔍 RAG 核心: {rag_core_path}")
    
    return True

def main():
    """主函数"""
    print("🚀 启动批量导入 GUI...")
    
    # 配置环境
    if not setup_environment():
        sys.exit(1)
    
    try:
        # 导入模块
        print("📦 导入模块...")
        
        # 导入 RAG 核心（将从正确的结构自动导入）
        try:
            from mcp_server_organized.src.rag_core import log
            print("✅ 从模块化结构导入 RAG 核心")
        except ImportError:
            try:
                from rag_core import log
                print("✅ 从原始结构导入 RAG 核心")
            except ImportError as e:
                print(f"❌ 导入 RAG 核心错误: {e}")
                sys.exit(1)
        
        # 导入服务
        from services.configuration_service import ConfigurationService
        from services.document_service import DocumentService
        print("✅ 服务导入成功")
        
        # 导入控制器
        from controllers.main_controller import MainController
        print("✅ 控制器导入成功")
        
        # 导入视图
        from views.main_view import MainView
        print("✅ 视图导入成功")
        
        # 导入 tkinter
        import tkinter as tk
        print("✅ Tkinter 导入成功")
        
        # 创建应用程序
        print("🏗️ 创建应用程序...")
        
        # 创建主窗口
        root = tk.Tk()
        root.title("批量导入 GUI - RAG 系统")
        root.geometry("1200x800")
        root.minsize(1000, 700)
        
        # 创建服务
        config_service = ConfigurationService()
        
        # 创建控制器
        controller = MainController(root, config_service)
        
        # 创建主视图
        main_view = MainView(root, controller)
        
        # 配置关闭
        def on_closing():
            try:
                controller.cleanup()
                root.destroy()
            except Exception as e:
                print(f"关闭过程中出错: {e}")
                root.destroy()
        
        root.protocol("WM_DELETE_WINDOW", on_closing)
        
        print("✅ 应用程序创建成功")
        print("🎉 启动图形界面...")
        
        # 运行应用程序
        root.mainloop()
        
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("\n🔧 解决方案:")
        print("1. 验证您在正确的目录中")
        print("2. 安装依赖项: pip install -r requirements.txt")
        print("3. 验证 MCP 服务器配置正确")
        sys.exit(1)
        
    except Exception as e:
        print(f"💥 运行应用程序时出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main() 