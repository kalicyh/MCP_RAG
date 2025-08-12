"""
用于显示详细统计信息的组件
显示处理、缓存和数据库信息
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Any
import sys
import os
from pathlib import Path

# 配置 sys.path 以进行绝对导入
current_dir = Path(__file__).parent.resolve()
project_root = current_dir.parent.parent.resolve()
sys.path.insert(0, str(current_dir.parent))
sys.path.insert(0, str(project_root))

class StatisticsWidget:
    """
    用于显示系统详细统计信息的组件
    """
    
    def __init__(self, parent):
        self.parent = parent
        self._create_widgets()
    
    def _create_widgets(self):
        """创建统计信息组件"""
        # 主框架
        self.frame = ttk.LabelFrame(self.parent, text="📊 系统统计信息")
        
        # 标签页控件
        self.notebook = ttk.Notebook(self.frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 处理标签页
        self.processing_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.processing_frame, text="处理")
        self._create_processing_tab()
        
        # 缓存标签页
        self.cache_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.cache_frame, text="缓存")
        self._create_cache_tab()
        
        # 数据库标签页
        self.database_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.database_frame, text="数据库")
        self._create_database_tab()
    
    def _create_processing_tab(self):
        """创建处理统计信息标签页"""
        # 带滚动的框架
        canvas = tk.Canvas(self.processing_frame, bg="#0D1117", highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.processing_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # 处理统计信息
        self.processing_labels = {}
        
        stats = [
            ("total_processed", "总计处理"),
            ("successful", "成功"),
            ("failed", "失败"),
            ("skipped", "跳过"),
            ("total_size", "总大小 (MB)")
        ]
        
        for i, (key, label) in enumerate(stats):
            ttk.Label(scrollable_frame, text=f"{label}:", font=("Arial", 10, "bold")).grid(
                row=i, column=0, sticky="w", padx=10, pady=5
            )
            self.processing_labels[key] = ttk.Label(scrollable_frame, text="0")
            self.processing_labels[key].grid(row=i, column=1, sticky="w", padx=10, pady=5)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def _create_cache_tab(self):
        """创建缓存统计信息标签页"""
        # 带滚动的框架
        canvas = tk.Canvas(self.cache_frame, bg="#0D1117", highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.cache_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # 缓存统计信息
        self.cache_labels = {}
        
        cache_stats = [
            ("total_requests", "总请求数"),
            ("memory_hits", "内存命中"),
            ("disk_hits", "磁盘命中"),
            ("misses", "未命中"),
            ("memory_hit_rate", "内存命中率"),
            ("overall_hit_rate", "总体命中率"),
            ("memory_cache_size", "内存缓存大小"),
            ("max_memory_size", "最大内存大小")
        ]
        
        for i, (key, label) in enumerate(cache_stats):
            ttk.Label(scrollable_frame, text=f"{label}:", font=("Arial", 10, "bold")).grid(
                row=i, column=0, sticky="w", padx=10, pady=5
            )
            self.cache_labels[key] = ttk.Label(scrollable_frame, text="N/A")
            self.cache_labels[key].grid(row=i, column=1, sticky="w", padx=10, pady=5)
        
        # 缓存操作按钮
        button_frame = ttk.Frame(scrollable_frame)
        button_frame.grid(row=len(cache_stats), column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="🔄 更新", command=self._update_cache_stats).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🗑️ 清理缓存", command=self._clear_cache).pack(side=tk.LEFT, padx=5)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def _create_database_tab(self):
        """创建数据库统计信息标签页"""
        # 带滚动的框架
        canvas = tk.Canvas(self.database_frame, bg="#0D1117", highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.database_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # 数据库统计信息
        self.database_labels = {}
        
        db_stats = [
            ("total_documents", "文档总数"),
            ("collection_name", "集合名称"),
            ("embedding_dimension", "嵌入维度"),
            ("is_large_database", "大型数据库"),
            ("current_memory_usage_mb", "内存使用 (MB)"),
            ("estimated_optimization_time", "预估优化时间"),
            ("recommended_optimization_approach", "推荐优化方式")
        ]
        
        for i, (key, label) in enumerate(db_stats):
            ttk.Label(scrollable_frame, text=f"{label}:", font=("Arial", 10, "bold")).grid(
                row=i, column=0, sticky="w", padx=10, pady=5
            )
            self.database_labels[key] = ttk.Label(scrollable_frame, text="N/A")
            self.database_labels[key].grid(row=i, column=1, sticky="w", padx=10, pady=5)
        
        # 数据库操作按钮
        button_frame = ttk.Frame(scrollable_frame)
        button_frame.grid(row=len(db_stats), column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="🔄 更新", command=self._update_database_stats).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="⚙️ 优化", command=self._optimize_database).pack(side=tk.LEFT, padx=5)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def update_processing_stats(self, stats: Dict[str, Any]):
        """更新处理统计信息"""
        if not stats:
            for key, label in self.processing_labels.items():
                label.config(text="0")
            return
        for key, label in self.processing_labels.items():
            value = stats.get(key, 0)
            if key == "total_size":
                # 转换字节为MB并显示两位小数
                value = f"{(value or 0) / (1024*1024):.2f}"
            else:
                value = int(value or 0)
            label.config(text=str(value))
    
    def update_cache_stats(self, stats: Dict[str, Any] = None):
        """更新缓存统计信息"""
        if stats is None or not stats:
            # Limpiar labels si no hay datos
            for key, label in self.cache_labels.items():
                label.config(text="N/A")
            return
        for key, label in self.cache_labels.items():
            value = stats.get(key, "N/A")
            label.config(text=str(value))
    
    def update_database_stats(self, stats: Dict[str, Any] = None):
        """更新数据库统计信息"""
        if stats is None:
            stats = {}
        for key, label in self.database_labels.items():
            value = stats.get(key, "N/A")
            if key == "is_large_database":
                value = "Sí" if value else "No"
            label.config(text=str(value))
    
    def _update_processing_stats(self):
        """更新处理统计信息的回调函数"""
        # 此方法将被控制器调用
        pass
    
    def _update_cache_stats(self):
        """更新缓存统计信息的回调函数"""
        # 此方法将被控制器调用
        pass
    
    def _update_database_stats(self):
        """更新数据库统计信息的回调函数"""
        # 此方法将被控制器调用
        pass
    
    def _clear_cache(self):
        """清理缓存的回调函数"""
        # 此方法将被控制器调用
        pass
    
    def _optimize_database(self):
        """优化数据库的回调函数"""
        # 此方法将被控制器调用
        pass
    
    def set_callbacks(self, callbacks: Dict[str, callable]):
        """设置操作回调函数"""
        if 'update_processing_stats' in callbacks:
            self._update_processing_stats = callbacks['update_processing_stats']
        if 'update_cache_stats' in callbacks:
            self._update_cache_stats = callbacks['update_cache_stats']
        if 'update_database_stats' in callbacks:
            self._update_database_stats = callbacks['update_database_stats']
        if 'clear_cache' in callbacks:
            self._clear_cache = callbacks['clear_cache']
        if 'optimize_database' in callbacks:
            self._optimize_database = callbacks['optimize_database']
    
    def pack(self, **kwargs):
        """打包组件"""
        self.frame.pack(**kwargs)
    
    def pack_forget(self):
        """取消打包组件"""
        self.frame.pack_forget() 