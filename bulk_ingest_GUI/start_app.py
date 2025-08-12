#!/usr/bin/env python3
"""
批量导入 GUI 启动脚本
无需相对导入即可运行
"""

import sys
import os
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

def setup_paths():
    """配置导入路径"""
    # 获取绝对路径
    script_path = Path(__file__).resolve()
    gui_dir = script_path.parent
    project_root = gui_dir.parent
    
    # 添加到 Python 路径
    sys.path.insert(0, str(gui_dir))
    sys.path.insert(0, str(project_root))
    
    return gui_dir, project_root

def create_simple_app():
    """创建简单应用程序进行测试"""
    print("🚀 创建简单应用程序...")
    
    # 创建主窗口
    root = tk.Tk()
    root.title("Bulk Ingest GUI - Prueba")
    root.geometry("800x600")
    
    # Frame principal
    main_frame = ttk.Frame(root)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    # Título
    title_label = ttk.Label(main_frame, text="Bulk Ingest GUI", font=("Arial", 16, "bold"))
    title_label.pack(pady=20)
    
    # Información
    info_text = """
    ✅ Aplicación iniciada correctamente
    
    📁 Directorio GUI: {gui_dir}
    📁 Directorio Proyecto: {project_root}
    🔍 rag_core.py encontrado: {rag_core_exists}
    
    🎯 Próximos pasos:
    1. Probar importación de rag_core.py
    2. Crear servicios y controladores
    3. Implementar interfaz completa
    """.format(
        gui_dir=gui_dir,
        project_root=project_root,
        rag_core_exists=rag_core_path.exists()
    )
    
    info_label = ttk.Label(main_frame, text=info_text, justify=tk.LEFT)
    info_label.pack(pady=20)
    
    # Botón para probar rag_core
    def test_rag_core():
        try:
            import rag_core
            messagebox.showinfo("成功", "✅ rag_core.py 导入成功")
        except Exception as e:
            messagebox.showerror("错误", f"❌ 导入 rag_core 错误: {e}")
    
    test_button = ttk.Button(main_frame, text="测试 rag_core.py", command=test_rag_core)
    test_button.pack(pady=10)
    
    # 关闭按钮
    def close_app():
        root.destroy()
    
    close_button = ttk.Button(main_frame, text="关闭", command=close_app)
    close_button.pack(pady=10)
    
    return root

def main():
    """主函数"""
    global gui_dir, project_root, rag_core_path
    
    print("🚀 启动批量导入 GUI...")
    
    # 配置路径
    gui_dir, project_root = setup_paths()
    rag_core_path = project_root / "rag_core.py"
    
    print(f"✅ 环境已配置:")
    print(f"   📁 GUI 目录: {gui_dir}")
    print(f"   📁 项目根目录: {project_root}")
    print(f"   🔍 rag_core.py: {rag_core_path.exists()}")
    
    if not rag_core_path.exists():
        print("❌ 错误: 未找到 rag_core.py")
        sys.exit(1)
    
    try:
        # 创建简单应用程序
        root = create_simple_app()
        
        print("✅ 应用程序创建成功")
        print("🎉 启动图形界面...")
        
        # 运行应用程序
        root.mainloop()
        
    except Exception as e:
        print(f"💥 运行应用程序时出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main() 