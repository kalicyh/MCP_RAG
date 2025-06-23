"""
Widget para mostrar estadísticas detalladas
Muestra información sobre procesamiento, cache y base de datos
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Any
import sys
import os
from pathlib import Path

# Configurar sys.path para importaciones absolutas
current_dir = Path(__file__).parent.resolve()
project_root = current_dir.parent.parent.resolve()
sys.path.insert(0, str(current_dir.parent))
sys.path.insert(0, str(project_root))

class StatisticsWidget:
    """
    Widget para mostrar estadísticas detalladas del sistema
    """
    
    def __init__(self, parent):
        self.parent = parent
        self._create_widgets()
    
    def _create_widgets(self):
        """Crea los widgets de estadísticas"""
        # Frame principal
        self.frame = ttk.LabelFrame(self.parent, text="📊 Estadísticas del Sistema")
        
        # Notebook para pestañas
        self.notebook = ttk.Notebook(self.frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Pestaña de procesamiento
        self.processing_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.processing_frame, text="Procesamiento")
        self._create_processing_tab()
        
        # Pestaña de cache
        self.cache_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.cache_frame, text="Cache")
        self._create_cache_tab()
        
        # Pestaña de base de datos
        self.database_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.database_frame, text="Base de Datos")
        self._create_database_tab()
    
    def _create_processing_tab(self):
        """Crea la pestaña de estadísticas de procesamiento"""
        # Frame con scroll
        canvas = tk.Canvas(self.processing_frame, bg="#0D1117", highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.processing_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Estadísticas de procesamiento
        self.processing_labels = {}
        
        stats = [
            ("total_processed", "Total procesados"),
            ("successful", "Exitosos"),
            ("failed", "Fallidos"),
            ("skipped", "Omitidos"),
            ("total_size", "Tamaño total (MB)")
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
        """Crea la pestaña de estadísticas de cache"""
        # Frame con scroll
        canvas = tk.Canvas(self.cache_frame, bg="#0D1117", highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.cache_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Estadísticas de cache
        self.cache_labels = {}
        
        cache_stats = [
            ("total_requests", "Total de solicitudes"),
            ("memory_hits", "Hits en memoria"),
            ("disk_hits", "Hits en disco"),
            ("misses", "Misses"),
            ("memory_hit_rate", "Tasa de hit en memoria"),
            ("overall_hit_rate", "Tasa de hit general"),
            ("memory_cache_size", "Tamaño en memoria"),
            ("max_memory_size", "Tamaño máximo")
        ]
        
        for i, (key, label) in enumerate(cache_stats):
            ttk.Label(scrollable_frame, text=f"{label}:", font=("Arial", 10, "bold")).grid(
                row=i, column=0, sticky="w", padx=10, pady=5
            )
            self.cache_labels[key] = ttk.Label(scrollable_frame, text="N/A")
            self.cache_labels[key].grid(row=i, column=1, sticky="w", padx=10, pady=5)
        
        # Botones de cache
        button_frame = ttk.Frame(scrollable_frame)
        button_frame.grid(row=len(cache_stats), column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="🔄 Actualizar", command=self._update_cache_stats).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🗑️ Limpiar Cache", command=self._clear_cache).pack(side=tk.LEFT, padx=5)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def _create_database_tab(self):
        """Crea la pestaña de estadísticas de base de datos"""
        # Frame con scroll
        canvas = tk.Canvas(self.database_frame, bg="#0D1117", highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.database_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Estadísticas de base de datos
        self.database_labels = {}
        
        db_stats = [
            ("total_documents", "Total de documentos"),
            ("collection_name", "Nombre de colección"),
            ("embedding_dimension", "Dimensión de embeddings"),
            ("is_large_database", "Base grande"),
            ("current_memory_usage_mb", "Uso de memoria (MB)"),
            ("estimated_optimization_time", "Tiempo estimado optimización"),
            ("recommended_optimization_approach", "Enfoque recomendado")
        ]
        
        for i, (key, label) in enumerate(db_stats):
            ttk.Label(scrollable_frame, text=f"{label}:", font=("Arial", 10, "bold")).grid(
                row=i, column=0, sticky="w", padx=10, pady=5
            )
            self.database_labels[key] = ttk.Label(scrollable_frame, text="N/A")
            self.database_labels[key].grid(row=i, column=1, sticky="w", padx=10, pady=5)
        
        # Botones de base de datos
        button_frame = ttk.Frame(scrollable_frame)
        button_frame.grid(row=len(db_stats), column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="🔄 Actualizar", command=self._update_database_stats).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="⚙️ Optimizar", command=self._optimize_database).pack(side=tk.LEFT, padx=5)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def update_processing_stats(self, stats: Dict[str, Any]):
        """Actualiza las estadísticas de procesamiento"""
        if not stats:
            for key, label in self.processing_labels.items():
                label.config(text="0")
            return
        for key, label in self.processing_labels.items():
            value = stats.get(key, 0)
            if key == "total_size":
                # Convertir bytes a MB y mostrar con dos decimales
                value = f"{(value or 0) / (1024*1024):.2f}"
            else:
                value = int(value or 0)
            label.config(text=str(value))
    
    def update_cache_stats(self, stats: Dict[str, Any] = None):
        """Actualiza las estadísticas de cache"""
        if stats is None or not stats:
            # Limpiar labels si no hay datos
            for key, label in self.cache_labels.items():
                label.config(text="N/A")
            return
        for key, label in self.cache_labels.items():
            value = stats.get(key, "N/A")
            label.config(text=str(value))
    
    def update_database_stats(self, stats: Dict[str, Any] = None):
        """Actualiza las estadísticas de base de datos"""
        if stats is None:
            stats = {}
        for key, label in self.database_labels.items():
            value = stats.get(key, "N/A")
            if key == "is_large_database":
                value = "Sí" if value else "No"
            label.config(text=str(value))
    
    def _update_processing_stats(self):
        """Callback para actualizar estadísticas de procesamiento"""
        # Este método será llamado por el controlador
        pass
    
    def _update_cache_stats(self):
        """Callback para actualizar estadísticas de cache"""
        # Este método será llamado por el controlador
        pass
    
    def _update_database_stats(self):
        """Callback para actualizar estadísticas de base de datos"""
        # Este método será llamado por el controlador
        pass
    
    def _clear_cache(self):
        """Callback para limpiar cache"""
        # Este método será llamado por el controlador
        pass
    
    def _optimize_database(self):
        """Callback para optimizar base de datos"""
        # Este método será llamado por el controlador
        pass
    
    def set_callbacks(self, callbacks: Dict[str, callable]):
        """Establece los callbacks para las acciones"""
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
        """Empaqueta el widget"""
        self.frame.pack(**kwargs)
    
    def pack_forget(self):
        """Desempaqueta el widget"""
        self.frame.pack_forget() 