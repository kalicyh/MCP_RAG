"""
用于验证GUI与MCP服务器集成的测试脚本
验证两个组件使用相同的数据库
"""

import sys
import os
from pathlib import Path

# 配置路径
current_dir = Path(__file__).parent.resolve()
project_root = current_dir.parent.resolve()
mcp_src_dir = project_root / "mcp_server_organized" / "src"

# 添加MCP服务器目录到路径
if str(mcp_src_dir) not in sys.path:
    sys.path.insert(0, str(mcp_src_dir))

def test_server_integration():
    """测试 GUI 与 MCP 服务器使用相同数据库"""
    
    print("🧪 测试 GUI 和 MCP 服务器集成...")
    print("=" * 60)
    
    try:
        # 1. 验证 MCP 服务器配置
        print("\n1. 验证 MCP 服务器配置...")
        from utils.config import Config
        
        print(f"   ✅ 配置已从以下位置加载: {mcp_src_dir}")
        print(f"   📁 数据目录: {Config.CONVERTED_DOCS_DIR}")
        print(f"   📊 向量存储: {Config.VECTOR_STORE_DIR}")
        print(f"   🧠 嵌入缓存: {Config.EMBEDDING_CACHE_DIR}")
        
        # 2. 验证目录是否存在
        print("\n2. 验证 MCP 服务器目录...")
        Config.ensure_directories()
        print("   ✅ MCP 服务器目录已创建/验证")
        
        # 3. 验证从 GUI 中 rag_core 工作
        print("\n3. 从 GUI 验证 rag_core...")
        import bulk_ingest_GUI.rag_core_wrapper as rag_wrapper
        
        # Probar importación
        functions = rag_wrapper.get_rag_functions()
        print("   ✅ Funciones de rag_core importadas correctamente")
        
        # 4. 验证两者使用相同的数据库
        print("\n4. Verificando consistencia de base de datos...")
        
        # 从MCP服务器获取数据库
        from rag_core import get_vector_store
        server_vector_store = get_vector_store()
        print("   ✅ 已获取MCP服务器数据库")
        
        # 从GUI获取数据库
        gui_vector_store = rag_wrapper.get_vector_store()
        print("   ✅ Base de datos de la GUI obtenida")
        
        # 验证它们是同一个实例
        if server_vector_store == gui_vector_store:
            print("   ✅ Ambos componentes usan la misma base de datos")
        else:
            print("   ❌ Los componentes usan bases de datos diferentes")
            return False
        
        # 5. 验证目录配置
        print("\n5. 验证目录配置...")
        
        # 验证GUI使用服务器的目录
        from bulk_ingest_GUI.gui_utils.constants import CONVERTED_DOCS_DIR, VECTOR_STORE_DIR, EMBEDDING_CACHE_DIR
        
        expected_docs_dir = str(project_root / "mcp_server_organized" / "data" / "documents")
        expected_vector_dir = str(project_root / "mcp_server_organized" / "data" / "vector_store")
        expected_cache_dir = str(project_root / "mcp_server_organized" / "embedding_cache")
        
        if CONVERTED_DOCS_DIR == expected_docs_dir:
            print("   ✅ GUI使用服务器的文档目录")
        else:
            print(f"   ❌ GUI使用了错误的目录: {CONVERTED_DOCS_DIR}")
            print(f"      Esperado: {expected_docs_dir}")
            return False
        
        if VECTOR_STORE_DIR == expected_vector_dir:
            print("   ✅ GUI使用服务器的向量数据库目录")
        else:
            print(f"   ❌ GUI使用了错误的目录: {VECTOR_STORE_DIR}")
            print(f"      Esperado: {expected_vector_dir}")
            return False
        
        if EMBEDDING_CACHE_DIR == expected_cache_dir:
            print("   ✅ GUI使用服务器的缓存目录")
        else:
            print(f"   ❌ GUI使用了错误的目录: {EMBEDDING_CACHE_DIR}")
            print(f"      Esperado: {expected_cache_dir}")
            return False
        
        # 6. 验证文档服务是否正常
        print("\n6. 验证文档服务...")
        from bulk_ingest_GUI.services.document_service import DocumentService
        from bulk_ingest_GUI.services.configuration_service import ConfigurationService
        
        config_service = ConfigurationService()
        doc_service = DocumentService(config_service)
        print("   ✅ 文档服务初始化成功")

        # 7. 验证数据库统计信息
        print("\n7. 验证数据库统计信息...")
        
        # 从服务器获取
        from rag_core import get_vector_store_stats
        server_stats = get_vector_store_stats(server_vector_store)
        print(f"   📊 服务器统计: {server_stats.get('total_documents', 0)} 个文档")
        
        # 从GUI获取
        gui_stats = doc_service.get_database_statistics()
        if 'error' not in gui_stats:
            print(f"   📊 GUI统计: {gui_stats.get('total_documents', 0)} 个文档")
            
            # 验证统计信息是否一致
            if server_stats.get('total_documents') == gui_stats.get('total_documents'):
                print("   ✅ 服务器和GUI统计数据一致")
            else:
                print("   ❌ 服务器和GUI统计数据不一致")
                return False
        else:
            print(f"   ❌ 获取GUI统计数据时出错: {gui_stats['error']}")
            return False
        
        print("\n" + "=" * 60)
        print("🎉 所有测试通过！GUI已正确集成到MCP服务器")
        print("✅ 两个组件使用同一个数据库")
        print("✅ 目录配置正确")
        print("✅ 统计信息一致")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_server_integration()
    sys.exit(0 if success else 1) 