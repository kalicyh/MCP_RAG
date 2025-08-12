"""
Bulk Ingest GUI 的常量与集中式配置
"""

import os
from pathlib import Path

APP_NAME = "批量导入 GUI"
VERSION = "1.0.0"

# =============================================================================
# 文件配置
# =============================================================================

# 支持的文件扩展名
SUPPORTED_EXTENSIONS = [
    # Office 文档
    ".pdf", ".docx", ".doc", ".pptx", ".ppt", ".xlsx", ".xls", ".rtf",
    # OpenDocument 文档
    ".odt", ".odp", ".ods",
    # 网页与标记格式
    ".html", ".htm", ".xml", ".md",
    # 纯文本格式
    ".txt", ".csv", ".tsv",
    # 数据格式
    ".json", ".yaml", ".yml",
    # 图片（需 OCR）
    ".png", ".jpg", ".jpeg", ".tiff", ".bmp",
    # 邮件
    ".eml", ".msg"
]

# 目录
# 使用 MCP 服务器组织的目录
current_dir = Path(__file__).parent.parent.resolve()
project_root = current_dir.parent.resolve()
mcp_server_dir = project_root / "mcp_server_organized"

CONVERTED_DOCS_DIR = str(mcp_server_dir / "data" / "documents")
EMBEDDING_CACHE_DIR = str(mcp_server_dir / "embedding_cache")
VECTOR_STORE_DIR = str(mcp_server_dir / "data" / "vector_store")
CONFIG_FILE = "bulk_ingest_config.json"

# =============================================================================
# 界面配置
# =============================================================================

# 窗口大小
DEFAULT_WINDOW_SIZE = "1100x850"
MIN_WINDOW_SIZE = (900, 700)

# “终端精致”主题颜色
COLORS = {
    'BG_COLOR': "#0D1117",           # 深色背景（GitHub Dark）
    'FG_COLOR': "#56F175",           # CRT 绿色
    'SELECT_BG': "#56F175",          # 选中背景绿色
    'SELECT_FG': "#0D1117",          # 选中文本黑色
    'TROUGH_COLOR': "#161B22",       # 进度条背景
    'BORDER_COLOR': "#30363D",       # 深灰色边框
    'HIGHLIGHT_BORDER': "#56F175",   # 悬停绿色边框
    'WARNING_COLOR': "#F1E056",      # 警告黄色
    'ERROR_COLOR': "#F85149",        # 错误红色
}

# 字体
FONT_FAMILY = "Consolas"
FONT_SIZES = {
    'title': 16,
    'subtitle': 11,
    'normal': 10,
    'small': 9
}

# =============================================================================
# 性能配置
# =============================================================================

# 内存与性能限制
PERFORMANCE_LIMITS = {
    'max_preview_length': 50000,     # 预览最大字符数
    'batch_size': 10,                # 每批处理文档数
    'memory_limit': 100 * 1024 * 1024,  # 100MB 内存限制
    'max_log_lines': 1000,           # 日志最大行数
    'update_interval': 100,          # UI 更新间隔（毫秒）
}

# =============================================================================
# 处理配置
# =============================================================================

# 分块配置
CHUNKING_CONFIG = {
    'default_chunk_size': 1000,
    'default_overlap': 200,
    'semantic_chunking': True,
}

# 存储配置
STORAGE_CONFIG = {
    'confirm_required': True,
    'batch_processing': True,
    'progress_update_interval': 0.5,  # 秒
}

# =============================================================================
# 消息与文本
# =============================================================================

MESSAGES = {
    'processing': {
        'start': "🚀 开始处理...",
        'complete': "✅ 处理完成",
        'error': "❌ 处理过程中出错",
        'stopped': "⏹️ 处理已停止",
    },
    'storage': {
        'start': "💾 开始存储...",
        'complete': "🎉 存储完成",
        'error': "❌ 存储过程中出错",
        'stopped': "⏹️ 存储已停止",
    },
    'ui': {
        'ready': "准备处理",
        'select_directory': "请选择一个目录",
        'no_documents': "没有可处理的文档",
        'confirm_storage': "请确认存储操作",
    }
}

# =============================================================================
# 校验
# =============================================================================

def is_supported_file(filename: str) -> bool:
    """判断文件扩展名是否支持"""
    return any(filename.lower().endswith(ext) for ext in SUPPORTED_EXTENSIONS)

def get_file_type(filename: str) -> str:
    """根据扩展名获取文件类型"""
    return os.path.splitext(filename)[1].lower()

def validate_directory(path: str) -> bool:
    """校验目录是否存在且可访问"""
    return os.path.isdir(path) and os.access(path, os.R_OK)