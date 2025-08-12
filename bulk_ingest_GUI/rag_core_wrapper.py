"""
rag_core 的包装器，确保正确导入
用于 Bulk Ingest GUI 的集成

此包装器确保 GUI 使用与 MCP 服务器相同的数据库，
以保持两个组件之间的数据一致性。
"""

import sys
import os
from pathlib import Path

def setup_rag_core_environment():
    """配置 rag_core 的运行环境"""
    # 获取路径
    current_dir = Path(__file__).parent.resolve()
    project_root = current_dir.parent.resolve()
    mcp_src_dir = project_root / "mcp_server_organized" / "src"
    # 配置 sys.path 以便 rag_core 能导入 utils.config
    if mcp_src_dir.exists():
        # 添加 MCP 服务器 src 目录到 path
        if str(mcp_src_dir) not in sys.path:
            sys.path.insert(0, str(mcp_src_dir))
        # 也添加父目录以支持相对导入
        mcp_parent = mcp_src_dir.parent
        if str(mcp_parent) not in sys.path:
            sys.path.insert(0, str(mcp_parent))
        print(f"✅ 已为 rag_core 配置环境: {mcp_src_dir}")
        return True
    else:
        print(f"❌ 未找到 MCP 服务器目录: {mcp_src_dir}")
        return False

def import_rag_core_functions():
    """导入 rag_core 所需的所有函数"""
    if not setup_rag_core_environment():
        raise ImportError("无法配置 rag_core 的环境")
    try:
        # 保存当前 path
        original_path = sys.path.copy()
        # 专门为 rag_core 配置 path
        current_dir = Path(__file__).parent.resolve()
        project_root = current_dir.parent.resolve()
        mcp_src_dir = project_root / "mcp_server_organized" / "src"
        # 临时 path 配置
        temp_path = [str(mcp_src_dir), str(mcp_src_dir.parent)]
        temp_path.extend(original_path)
        sys.path = temp_path
        # 临时切换到 MCP 服务器目录
        original_cwd = os.getcwd()
        os.chdir(mcp_src_dir)
        try:
            # 导入 MCP 服务器配置
            from utils.config import Config
            # 配置环境变量，确保使用同一数据库
            os.environ['RAG_DATA_DIR'] = str(project_root / "mcp_server_organized" / "data")
            os.environ['RAG_VECTOR_STORE_DIR'] = str(project_root / "mcp_server_organized" / "data" / "vector_store")
            os.environ['RAG_EMBEDDING_CACHE_DIR'] = str(project_root / "mcp_server_organized" / "embedding_cache")
            # 不要在 GUI 端调用 Config.ensure_directories()
            # 目录应由 MCP 服务器提前创建
            # Config.ensure_directories()
            # 优先从模块化结构导入
            from rag_core import (
                load_document_with_elements,
                add_text_to_knowledge_base_enhanced,
                get_vector_store,
                log,
                clear_embedding_cache,
                get_cache_stats,
                get_vector_store_stats_advanced
            )
            print("✅ 已从模块化结构导入 rag_core 函数")
            print(f"✅ 使用 MCP 服务器数据库: {Config.VECTOR_STORE_DIR}")
            return {
                'load_document_with_elements': load_document_with_elements,
                'add_text_to_knowledge_base_enhanced': add_text_to_knowledge_base_enhanced,
                'get_vector_store': get_vector_store,
                'log': log,
                'clear_embedding_cache': clear_embedding_cache,
                'get_cache_stats': get_cache_stats,
                'get_vector_store_stats_advanced': get_vector_store_stats_advanced
            }
        finally:
            # 恢复原工作目录
            os.chdir(original_cwd)
            # 恢复原 path
            sys.path = original_path
    except ImportError as e:
        print(f"❌ 从模块化结构导入失败: {e}")
        # 回退：尝试从原始 rag_core.py 导入
        try:
            from rag_core import (
                load_document_with_elements,
                add_text_to_knowledge_base_enhanced,
                get_vector_store,
                log,
                clear_embedding_cache,
                get_cache_stats,
                get_vector_store_stats_advanced
            )
            print("✅ 已从原始结构导入 rag_core 函数")
            return {
                'load_document_with_elements': load_document_with_elements,
                'add_text_to_knowledge_base_enhanced': add_text_to_knowledge_base_enhanced,
                'get_vector_store': get_vector_store,
                'log': log,
                'clear_embedding_cache': clear_embedding_cache,
                'get_cache_stats': get_cache_stats,
                'get_vector_store_stats_advanced': get_vector_store_stats_advanced
            }
        except ImportError as e2:
            print(f"❌ 从原始结构导入失败: {e2}")
            raise ImportError(f"无法导入 rag_core: {e2}")

# 全局变量
_rag_functions = None
_import_attempted = False

def get_rag_functions():
    """获取 rag_core 的所有函数，如有必要自动导入"""
    global _rag_functions, _import_attempted
    if _rag_functions is not None:
        return _rag_functions
    if _import_attempted:
        raise ImportError("rag_core 不可用")
    _import_attempted = True
    try:
        _rag_functions = import_rag_core_functions()
        return _rag_functions
    except ImportError as e:
        print(f"❌ 导入 rag_core 时出错: {e}")
        raise

# 动态导入的包装函数

def load_document_with_elements(*args, **kwargs):
    """load_document_with_elements 的包装器"""
    functions = get_rag_functions()
    return functions['load_document_with_elements'](*args, **kwargs)

def add_text_to_knowledge_base_enhanced(*args, **kwargs):
    """add_text_to_knowledge_base_enhanced 的包装器"""
    functions = get_rag_functions()
    return functions['add_text_to_knowledge_base_enhanced'](*args, **kwargs)

def get_vector_store(*args, **kwargs):
    """get_vector_store 的包装器 - 使用与 MCP 服务器相同的数据库"""
    functions = get_rag_functions()
    return functions['get_vector_store'](*args, **kwargs)

def log(*args, **kwargs):
    """log 的包装器"""
    functions = get_rag_functions()
    return functions['log'](*args, **kwargs)

def clear_embedding_cache(*args, **kwargs):
    """clear_embedding_cache 的包装器"""
    functions = get_rag_functions()
    return functions['clear_embedding_cache'](*args, **kwargs)

def get_cache_stats(*args, **kwargs):
    """get_cache_stats 的包装器"""
    functions = get_rag_functions()
    return functions['get_cache_stats'](*args, **kwargs)

def get_vector_store_stats_advanced(*args, **kwargs):
    """get_vector_store_stats_advanced 的包装器"""
    functions = get_rag_functions()
    return functions['get_vector_store_stats_advanced'](*args, **kwargs)

def optimize_vector_store(*args, **kwargs):
    print(">>> [包装器] 调用 optimize_vector_store")
    if not setup_rag_core_environment():
        raise ImportError("无法配置 rag_core 的环境")
    try:
        import importlib
        rag_core = importlib.import_module("rag_core")
        result = rag_core.optimize_vector_store(*args, **kwargs)
        print(f">>> [包装器] optimize_vector_store 结果: {result}")
        return result
    except Exception as e:
        print(f"❌ 调用 optimize_vector_store 时出错: {e}")
        return {"status": "error", "message": str(e)}