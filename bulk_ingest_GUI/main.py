"""
主程序文件 - 批量导入 GUI
启动应用程序并连接所有组件
"""

import sys
import os
from pathlib import Path

# 配置 sys.path 以支持绝对导入
current_dir = Path(__file__).parent.resolve()
project_root = current_dir.parent.resolve()
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(project_root))

# 导入常量，确保在 setup_environment 之前
from gui_utils.constants import APP_NAME, VERSION

def setup_environment():
    """配置应用程序环境"""
    # 使用 MCP 服务器的目录
    mcp_server_dir = project_root / "mcp_server_organized"
    
    # 确保 MCP 服务器目录存在
    try:
        # 导入 MCP 服务器配置
        from utils.config import Config
        
        # 确保目录存在
        Config.ensure_directories()
        
        print(f"[bold green]✅ MCP 服务器目录已验证:[/bold green]")
        print(f"[bold green]  📁 文档目录: {Config.CONVERTED_DOCS_DIR}[/bold green]")
        print(f"[bold green]  📁 向量存储: {Config.VECTOR_STORE_DIR}[/bold green]")
        print(f"[bold green]  📁 嵌入缓存: {Config.EMBEDDING_CACHE_DIR}[/bold green]")
        
    except ImportError as e:
        print(f"[bold yellow]⚠️ 无法导入 MCP 服务器配置: {e}[/bold yellow]")
        print(f"[bold yellow]  手动创建目录...[/bold yellow]")
        
        # 备用方案：手动创建目录
        server_directories = {
            "embedding_cache": mcp_server_dir / "embedding_cache",
            "vector_store": mcp_server_dir / "data" / "vector_store",
            "documents": mcp_server_dir / "data" / "documents"
        }
        
        for name, path in server_directories.items():
            path.mkdir(parents=True, exist_ok=True)
            print(f"[bold green]✅ 目录 {name}: {path}[/bold green]")
    
    print(f"[bold green]✅ {APP_NAME} v{VERSION} 环境已配置[/bold green]")
    print(f"[bold blue]📁 使用 MCP 服务器目录: {mcp_server_dir}[/bold blue]")

# 在导入任何使用 rag_core 的模块之前配置环境
setup_environment()

import tkinter as tk
from services.configuration_service import ConfigurationService
from controllers.main_controller import MainController
from views.main_view import MainView
from gui_utils.exceptions import BulkIngestError

# 导入 Rich 以增强控制台输出
from rich import print
from rich.panel import Panel


def create_application():
    """创建并配置主应用程序"""
    try:
        # 创建主窗口
        root = tk.Tk()
        
        # 配置窗口
        root.title(f"{APP_NAME} v{VERSION}")
        root.geometry("1200x800")
        root.minsize(1000, 700)
        
        # 如果图标存在，设置图标
        icon_path = current_dir / "assets" / "icon.ico"
        if icon_path.exists():
            try:
                root.iconbitmap(icon_path)
            except:
                pass  # 如果无法加载图标则忽略
        
        # 创建服务
        config_service = ConfigurationService()
        
        # 创建控制器
        controller = MainController(root, config_service)
        
        # 创建主视图
        main_view = MainView(root, controller)
        
        # 配置窗口关闭事件
        def on_closing():
            try:
                controller.cleanup()
                root.destroy()
            except Exception as e:
                print(Panel(f"[bold red]关闭时发生错误: {e}[/bold red]", title="[red]错误[/red]"))
                root.destroy()
        
        root.protocol("WM_DELETE_WINDOW", on_closing)
        
        return root, controller, main_view
        
    except Exception as e:
        print(Panel(f"[bold red]❌ 创建应用程序时发生错误: {e}[/bold red]", title="[red]错误[/red]"))
        raise


def main():
    """主函数，启动应用程序"""
    try:
        print(Panel(f"[bold blue]🚀 启动 {APP_NAME} v{VERSION}[/bold blue]", title="[cyan]启动[/cyan]"))
        print("[cyan]" + "=" * 50 + "[/cyan]")
        
        # 创建应用程序
        root, controller, main_view = create_application()
        
        print("[bold green]✅ 应用程序创建成功[/bold green]")
        print("[bold magenta]📋 可用功能:[/bold magenta]")
        print("[yellow]   • 使用 rag_core.py 处理文档[/yellow]")
        print("[yellow]   • 高级语义分块[/yellow]")
        print("[yellow]   • 优化的嵌入缓存[/yellow]")
        print("[yellow]   • 向量存储[/yellow]")
        print("[yellow]   • 导入/导出文档列表[/yellow]")
        print("[yellow]   • 过滤与搜索[/yellow]")
        print("[cyan]" + "=" * 50 + "[/cyan]")
        
        # 启动主循环
        root.mainloop()
        
    except Exception as e:
        print(Panel(f"[bold red]💥 应用程序发生致命错误: {e}[/bold red]", title="[red]致命错误[/red]"))
        print("[red]错误详情:[/red]")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()