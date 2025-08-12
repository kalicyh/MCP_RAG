"""
批量导入 GUI 应用程序的主视图
显示图形界面并连接 MainController
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from typing import List, Dict, Any
import sys
import os
from pathlib import Path
import queue
import tkinter.ttk as ttk_plus

# 配置 sys.path 以支持绝对导入
current_dir = Path(__file__).parent.resolve()
project_root = current_dir.parent.parent.resolve()
sys.path.insert(0, str(current_dir.parent))
sys.path.insert(0, str(project_root))

from controllers.main_controller import MainController
from widgets.document_preview_widget import DocumentPreviewWidget
from widgets.statistics_widget import StatisticsWidget

class MainView:
    """
    批量导入 GUI 应用程序的主视图
    """
    def __init__(self, root: tk.Tk, controller: MainController):
        self.root = root
        self.controller = controller
        
        # 配置主窗口
        self.root.title("批量导入高级版 - 模块化RAG系统")
        self.root.geometry("1100x850")
        self.root.minsize(900, 700)
        
        # 状态变量
        self.selected_directory = tk.StringVar()
        self.save_markdown = tk.BooleanVar(value=True)
        self.search_text = tk.StringVar()
        self.file_type_filter = tk.StringVar(value="全部")
        
        # 线程间安全日志记录队列
        self.log_queue = queue.Queue()
        self.storage_log_queue = queue.Queue()
        
        # 配置样式并创建组件
        self.setup_styles()
        self.create_widgets()
        
        # 将 UI 回调连接到控制器
        self._register_callbacks()
        
        # 开始处理日志队列
        self.process_log_queue()
        self.process_storage_log_queue()
        
        # 配置自动清理
        self.setup_cleanup()
    
    def setup_styles(self):
        """为界面配置'精致终端'主题样式。"""
        
        # --- "精致终端"调色板 ---
        BG_COLOR = "#0D1117"       # 蓝黑色，如现代终端 (GitHub Dark)
        FG_COLOR = "#56F175"       # CRT 绿色，微妙且可读
        SELECT_BG = "#56F175"      # 选择背景的绿色
        SELECT_FG = "#0D1117"      # 选择文本的黑色
        TROUGH_COLOR = "#161B22"    # 进度条背景
        BORDER_COLOR = "#30363D"   # 深灰边框，非常微妙
        HIGHLIGHT_BORDER = "#56F175" # 鼠标悬停时的绿色边框
        FONT_FAMILY = "Consolas"   # 控制台的理想字体
        
        self.root.configure(bg=BG_COLOR)
        
        style = ttk.Style()
        style.theme_use('clam')
        
        # --- 通用控件配置 ---
        style.configure('.',
                        background=BG_COLOR,
                        foreground=FG_COLOR,
                        fieldbackground=BG_COLOR,
                        bordercolor=BORDER_COLOR)
        
        # --- 特定样式配置 ---
        style.configure('TFrame', background=BG_COLOR)
        style.configure('Title.TLabel', font=(FONT_FAMILY, 16, 'bold'), foreground=FG_COLOR, background=BG_COLOR)
        style.configure('Subtitle.TLabel', font=(FONT_FAMILY, 11), foreground=FG_COLOR, background=BG_COLOR)
        style.configure('Info.TLabel', foreground="#56F175", background=BG_COLOR)
        style.configure('Warning.TLabel', foreground="#F1E056", background=BG_COLOR) # 黄色
        
        # LabelFrame 样式配置
        style.configure('TLabelFrame', background=BG_COLOR, bordercolor=BORDER_COLOR, borderwidth=1)
        style.configure('TLabelFrame.Label', foreground=FG_COLOR, background=BG_COLOR, font=(FONT_FAMILY, 11, 'bold'))
        
        # 按钮样式配置
        style.map('TButton',
                  background=[('active', '#161B22')],
                  foreground=[('active', FG_COLOR)],
                  bordercolor=[('active', HIGHLIGHT_BORDER)])
        style.configure('TButton',
                        font=(FONT_FAMILY, 11, 'bold'),
                        foreground=FG_COLOR,
                        background=BG_COLOR,
                        borderwidth=1,
                        relief="solid",
                        padding=[10, 5])
        
        # 标签页样式配置 (Notebook)
        style.configure('TNotebook', background=BG_COLOR, borderwidth=1, bordercolor=BORDER_COLOR)
        style.configure('TNotebook.Tab',
                        background=[BG_COLOR],
                        foreground=[FG_COLOR],
                        font=(FONT_FAMILY, 11, 'bold'),
                        padding=[10, 5],
                        relief="solid",
                        borderwidth=1)
        style.map('TNotebook.Tab',
                  background=[('selected', '#161B22'), ('active', '#21262D')],
                  bordercolor=[('selected', HIGHLIGHT_BORDER), ('active', BORDER_COLOR)])
        
        # 进度条样式配置
        style.configure('green.Horizontal.TProgressbar',
                        troughcolor=TROUGH_COLOR,
                        background=FG_COLOR,
                        bordercolor=BORDER_COLOR,
                        lightcolor=FG_COLOR,
                        darkcolor=FG_COLOR)
                        
        # 文本框样式配置
        style.configure('TEntry', foreground=FG_COLOR, insertcolor=FG_COLOR, borderwidth=1, relief="solid")
        style.map('TEntry', fieldbackground=[('readonly', TROUGH_COLOR)])

        # 复选框样式配置
        style.configure('TCheckbutton',
                        indicatorforeground=FG_COLOR,
                        indicatorbackground=BG_COLOR,
                        background=BG_COLOR,
                        foreground=FG_COLOR,
                        font=(FONT_FAMILY, 11))
        style.map('TCheckbutton',
                  indicatorbackground=[('selected', FG_COLOR), ('active', BG_COLOR)],
                  indicatorforeground=[('selected', BG_COLOR), ('active', FG_COLOR)])
    
    def create_widgets(self):
        """创建界面所有组件"""
        # 主框架与标签页笔记本
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 标签页 1: 配置与处理
        self.create_processing_tab()
        
        # 标签页 2: 审核与选择  
        self.create_review_tab()
        
        # 标签页 3: 最终存储
        self.create_storage_tab()
        
        # 绑定标签页切换事件
        self.notebook.bind('<<NotebookTabChanged>>', self.on_tab_changed)
    
    def on_tab_changed(self, event):
        """处理标签页切换"""
        current_tab = self.notebook.select()
        tab_index = self.notebook.index(current_tab)
        # 如果切换到存储标签页 (索引 2)，更新摘要
        if tab_index == 2:  # 存储标签页
            self._update_summary()
        # 如果切换到审核标签页 (索引 1)，更新处理统计信息
        if tab_index == 1 and hasattr(self, 'stats_widget'):
            stats = self.controller.get_processing_statistics()
            self.stats_widget.update_processing_stats(stats)
        # 如果切换到缓存标签页 (统计组件中的索引 1)
        if hasattr(self, 'stats_widget'):
            stats_tab = self.stats_widget.notebook.index(self.stats_widget.notebook.select())
            if stats_tab == 1:  # 缓存
                cache_stats = self.controller.get_cache_statistics()
                self.stats_widget.update_cache_stats(cache_stats)
            elif stats_tab == 2:  # 数据库
                db_stats = self.controller.get_database_statistics()
                self.stats_widget.update_database_stats(db_stats)
        # 同时在统计组件内部标签页切换时更新
        if hasattr(self, 'stats_widget'):
            def on_stats_tab_changed(event):
                stats_tab = self.stats_widget.notebook.index(self.stats_widget.notebook.select())
                if stats_tab == 1:
                    cache_stats = self.controller.get_cache_statistics()
                    self.stats_widget.update_cache_stats(cache_stats)
                elif stats_tab == 2:
                    db_stats = self.controller.get_database_statistics()
                    self.stats_widget.update_database_stats(db_stats)
            self.stats_widget.notebook.bind('<<NotebookTabChanged>>', on_stats_tab_changed)
    
    def create_processing_tab(self):
        """创建处理标签页"""
        processing_frame = ttk.Frame(self.notebook)
        self.notebook.add(processing_frame, text="📁 处理")
        
        # 目录部分
        self.create_directory_section(processing_frame)
        
        # 选项部分
        self.create_options_section(processing_frame)
        
        # 进度部分
        self.create_progress_section(processing_frame)
        
        # 日志部分
        self.create_logs_section(processing_frame)
        
        # 控制按钮
        self.create_control_buttons(processing_frame)
        
        # 摘要部分
        self.create_summary_section(processing_frame)
    
    def create_review_tab(self):
        """创建审核标签页"""
        review_frame = ttk.Frame(self.notebook)
        self.notebook.add(review_frame, text="📋 审核")
        
        # 顶部过滤器和控制框架
        top_frame = ttk.Frame(review_frame)
        top_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # 过滤器
        filter_frame = ttk.LabelFrame(top_frame, text="过滤器")
        filter_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(filter_frame, text="搜索:").pack(side=tk.LEFT, padx=5)
        search_entry = ttk.Entry(filter_frame, textvariable=self.search_text, width=30)
        search_entry.pack(side=tk.LEFT, padx=5)
        search_entry.bind('<KeyRelease>', lambda e: self._update_documents_list())
        search_entry_tooltip = ttk.Label(filter_frame, text="🔍 输入文件名的一部分以过滤列表。", foreground="#56F175", background="#0D1117")
        search_entry_tooltip.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(filter_frame, text="类型:").pack(side=tk.LEFT, padx=10)
        file_types = ["全部", ".pdf", ".docx", ".txt", ".md", ".xlsx", ".pptx"]
        file_type_menu = ttk.OptionMenu(filter_frame, self.file_type_filter, "全部", *file_types, 
                                       command=lambda _: self._update_documents_list())
        file_type_menu.pack(side=tk.LEFT, padx=5)
        file_type_tooltip = ttk.Label(filter_frame, text="📂 按文件扩展名过滤。", foreground="#56F175", background="#0D1117")
        file_type_tooltip.pack(side=tk.LEFT, padx=5)
        
        # 选择按钮
        ttk.Button(filter_frame, text="全选", command=self._select_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(filter_frame, text="全不选", command=self._deselect_all).pack(side=tk.LEFT, padx=5)
        selection_help = ttk.Label(filter_frame, text="您可以选择一个或多个文档进行预览或存储。", foreground="#56F175", background="#0D1117")
        selection_help.pack(side=tk.LEFT, padx=10)
        
        # 列表和预览主框架
        main_frame = ttk.Frame(review_frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 文档列表 (左侧)
        list_frame = ttk.LabelFrame(main_frame, text="已处理文档")
        list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        self.docs_listbox = tk.Listbox(list_frame, selectmode=tk.MULTIPLE, height=20)
        self.docs_listbox.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        
        docs_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.docs_listbox.yview)
        docs_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.docs_listbox.config(yscrollcommand=docs_scrollbar.set)
        
        # 绑定选择事件
        self.docs_listbox.bind('<<ListboxSelect>>', self._on_document_select)
        
        # 文档预览 (右侧)
        preview_frame = ttk.LabelFrame(main_frame, text="预览")
        preview_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # 创建预览组件
        self.preview_widget = DocumentPreviewWidget(preview_frame)
        self.preview_widget.pack(fill=tk.BOTH, expand=True)
        
        # 仅含统计信息的底部框架 (不含导航)
        bottom_frame = ttk.Frame(review_frame)
        bottom_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # 统计组件
        # self.stats_widget = StatisticsWidget(bottom_frame)
        # self.stats_widget.pack(side=tk.RIGHT)
        
        # 将统计组件回调函数与控制器连接
        # stats_callbacks = {
        #     'update_processing_stats': self._update_processing_stats_from_controller,
        #     'update_cache_stats': self._update_cache_stats_from_controller,
        #     'update_database_stats': self._update_database_stats_from_controller,
        #     'clear_cache': self._clear_cache_from_controller,
        #     'optimize_database': self._optimize_database_from_controller
        # }
        # self.stats_widget.set_callbacks(stats_callbacks)
    
    def create_storage_tab(self):
        """创建存储标签页"""
        storage_frame = ttk.Frame(self.notebook)
        self.notebook.add(storage_frame, text="💾 存储")
        
        # 存储选项
        self.create_storage_options(storage_frame)
        
        # 存储按钮
        self.create_storage_buttons(storage_frame)
        
        # 存储进度
        self.create_storage_progress_section(storage_frame)
        
        # 存储日志
        self.create_storage_logs(storage_frame)
        
        # 最终摘要
        self.create_final_summary_section(storage_frame)
    
    def create_directory_section(self, parent):
        """创建目录选择部分"""
        dir_frame = ttk.LabelFrame(parent, text="📁 文档目录")
        dir_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(dir_frame, text="路径:").pack(side=tk.LEFT, padx=5)
        dir_entry = ttk.Entry(dir_frame, textvariable=self.selected_directory, width=60)
        dir_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Button(dir_frame, text="浏览", command=self._browse_directory).pack(side=tk.LEFT, padx=5)
    
    def create_options_section(self, parent):
        """创建选项部分"""
        options_frame = ttk.LabelFrame(parent, text="⚙️ 处理选项")
        options_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Checkbutton(options_frame, text="保存Markdown副本", 
                       variable=self.save_markdown).pack(side=tk.LEFT, padx=10)
    
    def create_progress_section(self, parent):
        """创建进度部分"""
        progress_frame = ttk.LabelFrame(parent, text="📊 处理进度")
        progress_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, 
                                           maximum=100, style='green.Horizontal.TProgressbar')
        self.progress_bar.pack(fill=tk.X, padx=10, pady=5)
        
        self.progress_label = ttk.Label(progress_frame, text="进度: 0/0")
        self.progress_label.pack(side=tk.LEFT, padx=10)
    
    def create_logs_section(self, parent_frame):
        """创建日志部分"""
        log_frame = ttk.LabelFrame(parent_frame, text="📝 处理日志")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 日志控制按钮框架
        log_control_frame = ttk.Frame(log_frame)
        log_control_frame.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Button(log_control_frame, text="清除日志", 
                  command=self._clear_logs).pack(side=tk.LEFT, padx=2)
        
        # 文本区和滚动条框架
        text_scroll_frame = ttk.Frame(log_frame)
        text_scroll_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 日志文本区域
        self.log_text = tk.Text(text_scroll_frame, height=8, state=tk.DISABLED, 
                               bg="#0D1117", fg="#56F175", font=("Consolas", 9))
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbar para logs
        log_scrollbar = ttk.Scrollbar(text_scroll_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=log_scrollbar.set)
    
    def create_control_buttons(self, parent):
        """创建控制按钮"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.process_button = ttk.Button(button_frame, text="🚀 开始处理", 
                                        command=self._start_processing)
        self.process_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(button_frame, text="⏹️ 停止", 
                                     command=self._stop_processing, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="🧹 清理", command=self._clear_documents).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="📋 转到审核", command=self._go_to_review).pack(side=tk.RIGHT, padx=5)
    
    def create_summary_section(self, parent):
        """创建摘要部分"""
        summary_frame = ttk.LabelFrame(parent, text="📈 处理摘要")
        summary_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.summary_label = ttk.Label(summary_frame, text="摘要: 已处理 0 个文档")
        self.summary_label.pack(side=tk.LEFT, padx=10, pady=5)
    
    def create_storage_options(self, parent):
        """创建存储选项"""
        options_frame = ttk.LabelFrame(parent, text="⚙️ 存储选项")
        options_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(options_frame, text="选择要存储到知识库的文档。").pack(padx=10, pady=5)
    
    def create_storage_buttons(self, parent):
        """创建存储按钮"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.store_button = ttk.Button(button_frame, text="💾 存储所选文档", 
                                      command=self._start_storage)
        self.store_button.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="📤 导出列表", command=self._export_documents).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="📥 导入列表", command=self._import_documents).pack(side=tk.LEFT, padx=5)
    
    def create_storage_progress_section(self, parent):
        """创建存储进度部分"""
        progress_frame = ttk.LabelFrame(parent, text="📊 存储进度")
        progress_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.storage_progress_var = tk.DoubleVar()
        self.storage_progress_bar = ttk.Progressbar(progress_frame, variable=self.storage_progress_var, 
                                                   maximum=100, style='green.Horizontal.TProgressbar')
        self.storage_progress_bar.pack(fill=tk.X, padx=10, pady=5)
        
        self.storage_progress_label = ttk.Label(progress_frame, text="进度: 0/0")
        self.storage_progress_label.pack(side=tk.LEFT, padx=10)
    
    def create_storage_logs(self, parent_frame):
        """创建存储日志"""
        log_frame = ttk.LabelFrame(parent_frame, text="📝 存储日志")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 文本和滚动条内部框架
        text_scroll_frame = ttk.Frame(log_frame)
        text_scroll_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 存储日志文本区域
        self.storage_log_text = tk.Text(text_scroll_frame, height=6, state=tk.DISABLED, 
                                       bg="#0D1117", fg="#56F175", font=("Consolas", 9))
        self.storage_log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbar para logs de almacenamiento
        storage_log_scrollbar = ttk.Scrollbar(text_scroll_frame, orient=tk.VERTICAL, command=self.storage_log_text.yview)
        storage_log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.storage_log_text.config(yscrollcommand=storage_log_scrollbar.set)
    
    def create_final_summary_section(self, parent):
        """创建最终摘要部分"""
        summary_frame = ttk.LabelFrame(parent, text="📈 最终摘要")
        summary_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.final_summary_label = ttk.Label(summary_frame, text="摘要: 已准备存储 0 个文档")
        self.final_summary_label.pack(side=tk.LEFT, padx=10, pady=5)
    
    def _register_callbacks(self):
        """在控制器中注册UI回调函数"""
        callbacks = {
            'update_progress': self._update_progress,
            'update_logs': self._update_logs,
            'update_storage_logs': self._update_storage_logs,
            'update_status': self._update_status,
            'update_documents_list': self._update_documents_list,
            'update_summary': self._update_summary,
            'enable_processing_buttons': self._enable_processing_buttons,
            'disable_processing_buttons': self._disable_processing_buttons,
            'enable_storage_buttons': self._enable_storage_buttons,
            'disable_storage_buttons': self._disable_storage_buttons,
            'show_message': self._show_message,
            'update_storage_progress': self._update_storage_progress
        }
        self.controller.set_ui_callbacks(callbacks)
    
    # UI与控制器交互方法
    def _browse_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.selected_directory.set(directory)
    
    def _start_processing(self):
        self.controller.start_processing(self.selected_directory.get(), self.save_markdown.get())
    
    def _stop_processing(self):
        self.controller.stop_processing()
    
    def _clear_documents(self):
        self.controller.cleanup()
        self._update_documents_list()
        self._update_summary()
        self.preview_widget.clear_preview()
    
    def _go_to_review(self):
        self.notebook.select(1)  # Cambiar a pestaña de revisión
    
    def _select_all(self):
        self.controller.select_all_documents()
        self._update_documents_list()
    
    def _deselect_all(self):
        self.controller.deselect_all_documents()
        self._update_documents_list()
    
    def _start_storage(self):
        # Usar la selección lógica, no solo la visual
        selected_docs = self.controller.get_selected_documents()
        self.controller.start_storage(selected_docs)
    
    def _export_documents(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if file_path:
            docs = self.controller.get_processed_documents()
            self.controller.export_documents(docs, file_path)
    
    def _import_documents(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if file_path:
            self.controller.import_documents(file_path)
            self._update_documents_list()
    
    def _on_document_select(self, event):
        """点击时切换存储选择状态并预览文档"""
        selection = self.docs_listbox.curselection()
        if not hasattr(self, 'filtered_docs'):
            self.filtered_docs = self.controller.get_processed_documents()
        all_docs = self.controller.get_processed_documents()
        if selection:
            for idx in selection:
                if idx < len(self.filtered_docs):
                    doc = self.filtered_docs[idx]
                    # 在完整列表中查找真实对象并更新
                    for real_doc in all_docs:
                        if real_doc.file_path == doc.file_path:
                            real_doc.selected.set(not real_doc.selected.get())
                            # 预览选中的文档
                            self.preview_widget.show_document(real_doc)
                            break
            self._update_documents_list()
    
    def _clear_logs(self):
        """清理处理日志"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    # UI更新方法 (由控制器调用)
    def _update_progress(self, current, total, current_file=""):
        percent = (current / total * 100) if total > 0 else 0
        self.progress_var.set(percent)
        self.progress_label.config(text=f"进度: {current}/{total} - {current_file}")
        self.root.update_idletasks()
    
    def _update_logs(self, message):
        self.log_queue.put(message)
    
    def _update_storage_logs(self, message):
        self.storage_log_queue.put(message)
    
    def _update_status(self, status):
        # 根据状态更新界面状态
        pass
    
    def _update_documents_list(self):
        """根据搜索和类型过滤器更新文档列表"""
        self.docs_listbox.delete(0, tk.END)
        # 获取过滤器
        search = self.search_text.get().strip()
        file_type = self.file_type_filter.get()
        # 使用控制器的过滤方法
        filtered_docs = self.controller.filter_documents(search_text=search, file_type_filter=file_type)
        self.filtered_docs = filtered_docs  # 保存以供选择
        for doc in filtered_docs:
            status = "✅" if doc.selected.get() else "⭕"
            display_text = f"{status} {doc.original_name} ({doc.file_type}) - {doc.size_kb:.1f}KB"
            self.docs_listbox.insert(tk.END, display_text)
        if not filtered_docs:
            self.docs_listbox.insert(tk.END, "没有符合筛选条件的文档。")
    
    def _update_summary(self):
        """更新文档摘要"""
        documents = self.controller.get_processed_documents()
        total_size = sum(doc.size_kb for doc in documents)
        total_words = sum(doc.metadata.word_count for doc in documents)
        
        summary_text = f"摘要: {len(documents)} 个文档已处理 - {total_size:.1f}KB - {total_words:,} 个词"
        self.summary_label.config(text=summary_text)
        
        # 同时更新最终摘要
        final_summary_text = f"摘要: {len(documents)} 个文档已准备存储"
        self.final_summary_label.config(text=final_summary_text)
    
    def _enable_processing_buttons(self):
        self.process_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
    
    def _disable_processing_buttons(self):
        self.process_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
    
    def _enable_storage_buttons(self):
        self.store_button.config(state=tk.NORMAL)
    
    def _disable_storage_buttons(self):
        self.store_button.config(state=tk.DISABLED)
    
    def _show_message(self, title, message, msg_type="info"):
        if msg_type == "error":
            messagebox.showerror(title, message)
        elif msg_type == "warning":
            messagebox.showwarning(title, message)
        else:
            messagebox.showinfo(title, message)
    
    def _update_storage_progress(self, current, total, current_file=""):
        percent = (current / total * 100) if total > 0 else 0
        self.storage_progress_var.set(percent)
        self.storage_progress_label.config(text=f"进度: {current}/{total} - {current_file}")
        self.root.update_idletasks()
    
    def process_log_queue(self):
        """处理处理日志队列"""
        try:
            while True:
                message = self.log_queue.get_nowait()
                self.log_text.config(state=tk.NORMAL)
                self.log_text.insert(tk.END, message + "\n")
                self.log_text.see(tk.END)
                self.log_text.config(state=tk.DISABLED)
        except queue.Empty:
            pass
        finally:
            self.root.after(100, self.process_log_queue)
    
    def process_storage_log_queue(self):
        """处理存储日志队列"""
        try:
            while True:
                message = self.storage_log_queue.get_nowait()
                self.storage_log_text.config(state=tk.NORMAL)
                self.storage_log_text.insert(tk.END, message + "\n")
                self.storage_log_text.see(tk.END)
                self.storage_log_text.config(state=tk.DISABLED)
        except queue.Empty:
            pass
        finally:
            self.root.after(100, self.process_storage_log_queue)
    
    def setup_cleanup(self):
        """配置自动清理"""
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
    
    def _on_close(self):
        """处理应用程序关闭"""
        self.controller.cleanup()
        self.root.destroy()
    
    # 统计组件的回调方法
    def _update_processing_stats_from_controller(self):
        """从控制器更新处理统计信息"""
        try:
            stats = self.controller.get_processing_statistics()
            self.stats_widget.update_processing_stats(stats)
        except Exception as e:
            print(f"更新处理统计信息时出错: {e}")
    
    def _update_cache_stats_from_controller(self):
        """从控制器更新缓存统计信息"""
        try:
            stats = self.controller.get_cache_statistics()
            self.stats_widget.update_cache_stats(stats)
        except Exception as e:
            print(f"更新缓存统计信息时出错: {e}")
    
    def _update_database_stats_from_controller(self):
        print(">>> [GUI] 更新按钮已按下")
        try:
            stats = self.controller.get_database_statistics()
            print(f">>> [GUI] 统计信息已更新: {stats}")
            self.stats_widget.update_database_stats(stats)
        except Exception as e:
            print(f"更新数据库统计信息时出错: {e}")
    
    def _clear_cache_from_controller(self):
        """从控制器清理缓存"""
        try:
            result = self.controller.clear_cache()
            if result['status'] == 'success':
                # 清理后更新缓存统计信息
                self._update_cache_stats_from_controller()
        except Exception as e:
            print(f"清理缓存时出错: {e}")
    
    def _optimize_database_from_controller(self):
        print(">>> [GUI] 优化按钮已按下")
        try:
            result = self.controller.optimize_database()
            print(f">>> [GUI] 优化结果: {result}")
            self._update_database_stats_from_controller()
            msg = result.get('message', '优化已完成')
            status = result.get('status', 'success')
            if hasattr(self, 'ui_callbacks') and 'show_message' in self.ui_callbacks:
                tipo = 'info' if status == 'success' else 'error'
                self.ui_callbacks['show_message']("优化", msg, tipo)
        except Exception as e:
            print(f"优化数据库时出错: {e}")