#!/usr/bin/env python3
"""
实用工具单元测试。
测试系统维护和统计功能。
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# 将 src 目录添加到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

class TestUtilityTools(unittest.TestCase):
    """实用工具测试。"""
    
    def setUp(self):
        """每个测试的初始设置。"""
        # 导入要测试的函数
        from tools.utility_tools import (
            get_knowledge_base_stats, get_embedding_cache_stats,
            clear_embedding_cache_tool, optimize_vector_database,
            get_vector_database_stats, reindex_vector_database
        )
        
        self.get_knowledge_base_stats = get_knowledge_base_stats
        self.get_embedding_cache_stats = get_embedding_cache_stats
        self.clear_embedding_cache_tool = clear_embedding_cache_tool
        self.optimize_vector_database = optimize_vector_database
        self.get_vector_database_stats = get_vector_database_stats
        self.reindex_vector_database = reindex_vector_database
        
        # 设置模拟 RAG 状态
        self.mock_rag_state = {
            "vector_store": Mock(),
            "initialized": True
        }
        
        # 配置向量存储模拟
        self.mock_vector_store = Mock()
        self.mock_vector_store.get.return_value = {
            "documents": ["doc1", "doc2", "doc3"],
            "total_count": 3,
            "metadata": {"sources": ["source1.txt", "source2.txt"]}
        }
        
        self.mock_rag_state["vector_store"] = self.mock_vector_store
        
        # 配置状态
        from tools.utility_tools import set_rag_state
        set_rag_state(self.mock_rag_state)
    
    def test_get_knowledge_base_stats_basic(self):
        """测试 get_knowledge_base_stats 的基本功能。"""
        result = self.get_knowledge_base_stats()
        
        # 验证是否调用了向量存储
        self.mock_vector_store.get.assert_called_once()
        
        # 验证结果包含统计信息
        self.assertIsNotNone(result)
        self.assertIn("统计", result.lower() or "stats" in result.lower())
    
    def test_get_knowledge_base_stats_no_rag_state(self):
        """测试 get_knowledge_base_stats 处理未配置的RAG状态。"""
        from tools.utility_tools import set_rag_state
        set_rag_state({})  # 空状态
        
        result = self.get_knowledge_base_stats()
        
        # 应该处理未初始化的RAG状态
        self.assertIsNotNone(result)
        self.assertIn("error", result.lower() or "初始化" in result.lower())
    
    def test_get_knowledge_base_stats_vector_store_failure(self):
        """测试 get_knowledge_base_stats 处理向量存储失败。"""
        # 配置模拟对象抛出异常
        self.mock_vector_store.get.side_effect = Exception("数据库错误")
        
        result = self.get_knowledge_base_stats()
        
        # 应该处理向量存储错误
        self.assertIsNotNone(result)
        self.assertIn("error", result.lower())
    
    def test_get_embedding_cache_stats_basic(self):
        """测试 get_embedding_cache_stats 的基本功能。"""
        result = self.get_embedding_cache_stats()
        
        # 验证结果包含缓存统计信息
        self.assertIsNotNone(result)
        self.assertIn("cache", result.lower() or "统计" in result.lower())
    
    def test_clear_embedding_cache_tool_basic(self):
        """测试 clear_embedding_cache_tool 的基本功能。"""
        result = self.clear_embedding_cache_tool()
        
        # 验证结果表示清理成功
        self.assertIsNotNone(result)
        self.assertIn("清理", result.lower() or "cache" in result.lower())
    
    def test_optimize_vector_database_basic(self):
        """测试 optimize_vector_database 的基本功能。"""
        result = self.optimize_vector_database()
        
        # 验证结果表示优化成功
        self.assertIsNotNone(result)
        self.assertIn("优化", result.lower() or "优化" in result.lower())
    
    def test_get_vector_database_stats_basic(self):
        """测试 get_vector_database_stats 的基本功能。"""
        result = self.get_vector_database_stats()
        
        # 验证结果包含数据库统计信息
        self.assertIsNotNone(result)
        self.assertIn("统计", result.lower() or "stats" in result.lower())
    
    def test_reindex_vector_database_basic(self):
        """测试 reindex_vector_database 的基本功能。"""
        result = self.reindex_vector_database(profile="auto")
        
        # 验证结果表示重建索引成功
        self.assertIsNotNone(result)
        self.assertIn("重建索引", result.lower() or "reindex" in result.lower())
    
    def test_reindex_vector_database_custom_profile(self):
        """测试 reindex_vector_database 使用自定义配置文件。"""
        result = self.reindex_vector_database(profile="large")
        
        # 验证结果表示重建索引成功
        self.assertIsNotNone(result)
        self.assertIn("重建索引", result.lower() or "reindex" in result.lower())
    
    def test_error_handling_optimization_failure(self):
        """测试优化失败时的错误处理。"""
        # 模拟优化失败
        with patch('tools.utility_tools.optimize_vector_store') as mock_optimize:
            mock_optimize.side_effect = Exception("优化错误")
            
            result = self.optimize_vector_database()
            
            # 应该处理优化错误
            self.assertIsNotNone(result)
            self.assertIn("error", result.lower())
    
    def test_error_handling_reindex_failure(self):
        """测试重建索引失败时的错误处理。"""
        # 模拟重建索引失败
        with patch('tools.utility_tools.reindex_vector_store') as mock_reindex:
            mock_reindex.side_effect = Exception("重建索引错误")
            
            result = self.reindex_vector_database(profile="auto")
            
            # 应该处理重建索引错误
            self.assertIsNotNone(result)
            self.assertIn("error", result.lower())

class TestUtilityToolsConfiguration(unittest.TestCase):
    """实用工具配置测试。"""
    
    def test_set_rag_state(self):
        """测试 set_rag_state 函数。"""
        from tools.utility_tools import set_rag_state, rag_state
        
        test_state = {"test": "value", "initialized": True}
        set_rag_state(test_state)
        
        # 验证状态配置正确
        self.assertEqual(rag_state, test_state)
    
    def test_rag_state_persistence(self):
        """测试RAG状态在调用间的持久性。"""
        from tools.utility_tools import set_rag_state, rag_state
        
        # 配置初始状态
        initial_state = {"vector_store": "test_store", "initialized": True}
        set_rag_state(initial_state)
        
        # 验证状态保持不变
        self.assertEqual(rag_state, initial_state)
        
        # 修改状态
        modified_state = {"vector_store": "new_store", "initialized": True}
        set_rag_state(modified_state)
        
        # 验证状态已更新
        self.assertEqual(rag_state, modified_state)

class TestUtilityToolsIntegration(unittest.TestCase):
    """实用工具集成测试。"""
    
    def test_cache_statistics_integration(self):
        """测试缓存统计集成功能。"""
        from tools.utility_tools import get_embedding_cache_stats, clear_embedding_cache_tool
        
        # 获取初始统计信息
        initial_stats = get_embedding_cache_stats()
        self.assertIsNotNone(initial_stats)
        
        # 清理缓存
        clear_result = clear_embedding_cache_tool()
        self.assertIsNotNone(clear_result)
        self.assertIn("清理", clear_result.lower())
        
        # 获取清理后的统计信息
        final_stats = get_embedding_cache_stats()
        self.assertIsNotNone(final_stats)
    
    def test_database_optimization_workflow(self):
        """测试数据库优化工作流程。"""
        from tools.utility_tools import (
            get_vector_database_stats, 
            optimize_vector_database, 
            reindex_vector_database
        )
        
        # 获取初始统计信息
        initial_stats = get_vector_database_stats()
        self.assertIsNotNone(initial_stats)
        
        # 优化数据库
        optimize_result = optimize_vector_database()
        self.assertIsNotNone(optimize_result)
        self.assertIn("优化", optimize_result.lower())
        
        # 重建数据库索引
        reindex_result = reindex_vector_database(profile="auto")
        self.assertIsNotNone(reindex_result)
        self.assertIn("重建索引", reindex_result.lower())
        
        # 获取最终统计信息
        final_stats = get_vector_database_stats()
        self.assertIsNotNone(final_stats)
    
    def test_comprehensive_system_maintenance(self):
        """测试系统全面维护。"""
        from tools.utility_tools import (
            get_knowledge_base_stats,
            get_embedding_cache_stats,
            clear_embedding_cache_tool,
            optimize_vector_database,
            get_vector_database_stats,
            reindex_vector_database
        )
        
        # 1. 获取初始统计信息
        kb_stats = get_knowledge_base_stats()
        cache_stats = get_embedding_cache_stats()
        db_stats = get_vector_database_stats()
        
        self.assertIsNotNone(kb_stats)
        self.assertIsNotNone(cache_stats)
        self.assertIsNotNone(db_stats)
        
        # 2. 执行维护操作
        clear_result = clear_embedding_cache_tool()
        optimize_result = optimize_vector_database()
        reindex_result = reindex_vector_database(profile="auto")
        
        self.assertIsNotNone(clear_result)
        self.assertIsNotNone(optimize_result)
        self.assertIsNotNone(reindex_result)
        
        # 3. 验证所有操作都成功
        self.assertIn("清理", clear_result.lower())
        self.assertIn("优化", optimize_result.lower())
        self.assertIn("重建索引", reindex_result.lower())

class TestUtilityToolsEdgeCases(unittest.TestCase):
    """实用工具边界情况测试。"""
    
    def test_empty_vector_store_stats(self):
        """测试空向量存储的统计信息。"""
        from tools.utility_tools import get_knowledge_base_stats, set_rag_state
        
        # 配置空向量存储
        empty_vector_store = Mock()
        empty_vector_store.get.return_value = {
            "documents": [],
            "total_count": 0,
            "metadata": {}
        }
        
        empty_state = {"vector_store": empty_vector_store, "initialized": True}
        set_rag_state(empty_state)
        
        result = get_knowledge_base_stats()
        
        # 应该处理空向量存储
        self.assertIsNotNone(result)
        self.assertIn("0", result or "空" in result.lower())
    
    def test_large_vector_store_stats(self):
        """测试大型向量存储的统计信息。"""
        from tools.utility_tools import get_knowledge_base_stats, set_rag_state
        
        # 配置大型向量存储
        large_vector_store = Mock()
        large_vector_store.get.return_value = {
            "documents": ["doc" + str(i) for i in range(1000)],
            "total_count": 1000,
            "metadata": {"sources": ["source" + str(i) + ".txt" for i in range(100)]}
        }
        
        large_state = {"vector_store": large_vector_store, "initialized": True}
        set_rag_state(large_state)
        
        result = get_knowledge_base_stats()
        
        # 应该处理大型向量存储
        self.assertIsNotNone(result)
        self.assertIn("1000", result or "大" in result.lower())
    
    def test_invalid_profile_reindex(self):
        """测试使用无效配置文件重建索引。"""
        from tools.utility_tools import reindex_vector_database
        
        result = reindex_vector_database(profile="invalid_profile")
        
        # 应该处理无效配置文件
        self.assertIsNotNone(result)
        # 可能返回错误或使用默认配置文件
        self.assertTrue(len(result) > 0)

if __name__ == '__main__':
    unittest.main() 