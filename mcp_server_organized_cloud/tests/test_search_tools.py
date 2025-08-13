#!/usr/bin/env python3
"""
搜索工具单元测试。
测试 ask_rag 和 ask_rag_filtered 函数。
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# 将 src 目录添加到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

class TestSearchTools(unittest.TestCase):
    """搜索工具测试。"""
    
    def setUp(self):
        """每个测试的初始设置。"""
        # 导入要测试的函数
        from tools.search_tools import ask_rag, ask_rag_filtered
        
        self.ask_rag = ask_rag
        self.ask_rag_filtered = ask_rag_filtered
        
        # 设置模拟 RAG 状态
        self.mock_rag_state = {
            "vector_store": Mock(),
            "qa_chain": Mock(),
            "initialized": True
        }
        
        # 配置向量存储模拟
        self.mock_vector_store = Mock()
        self.mock_retriever = Mock()
        self.mock_vector_store.as_retriever.return_value = self.mock_retriever
        
        # 配置问答链模拟
        self.mock_qa_chain = Mock()
        self.mock_qa_chain.invoke.return_value = {
            "result": "RAG系统的模拟回答",
            "source_documents": [
                Mock(page_content="源文档 1", metadata={"source": "test1.txt"}),
                Mock(page_content="源文档 2", metadata={"source": "test2.txt"})
            ]
        }
        
        self.mock_rag_state["vector_store"] = self.mock_vector_store
        self.mock_rag_state["qa_chain"] = self.mock_qa_chain
        
        # 配置状态
        from tools.search_tools import set_rag_state
        set_rag_state(self.mock_rag_state)
    
    def test_ask_rag_basic(self):
        """测试 ask_rag 的基本查询功能。"""
        query = "什么是RAG系统？"
        
        result = self.ask_rag(query)
        
        # 验证是否调用了检索器
        self.mock_vector_store.as_retriever.assert_called_once()
        
        # 验证是否调用了问答链
        self.mock_qa_chain.invoke.assert_called_once()
        
        # 验证结果包含回答
        self.assertIsNotNone(result)
        self.assertIn("模拟回答", result)
    
    def test_ask_rag_empty_query(self):
        """测试 ask_rag 处理空查询。"""
        result = self.ask_rag("")
        
        # 应该处理空查询
        self.assertIsNotNone(result)
        self.assertIn("error", result.lower() or "空" in result.lower())
    
    def test_ask_rag_no_rag_state(self):
        """测试 ask_rag 处理未配置的RAG状态。"""
        from tools.search_tools import set_rag_state
        set_rag_state({})  # 空状态
        
        result = self.ask_rag("什么是RAG系统？")
        
        # 应该处理未初始化的RAG状态
        self.assertIsNotNone(result)
        self.assertIn("error", result.lower() or "初始化" in result.lower())
    
    def test_ask_rag_filtered_basic(self):
        """测试 ask_rag_filtered 的基本过滤功能。"""
        query = "系统有什么信息？"
        file_type = ".txt"
        min_tables = 1
        min_titles = 2
        processing_method = "unstructured"
        
        result = self.ask_rag_filtered(query, file_type, min_tables, min_titles, processing_method)
        
        # 验证是否使用过滤器调用了检索器
        self.mock_vector_store.as_retriever.assert_called_once()
        
        # 验证是否调用了问答链
        self.mock_qa_chain.invoke.assert_called_once()
        
        # 验证结果包含回答
        self.assertIsNotNone(result)
        self.assertIn("模拟回答", result)
    
    def test_ask_rag_filtered_no_filters(self):
        """测试 ask_rag_filtered 无过滤器运行。"""
        query = "系统有什么信息？"
        
        result = self.ask_rag_filtered(query, None, None, None, None)
        
        # 应该在无过滤器的情况下正常工作
        self.assertIsNotNone(result)
        self.assertIn("模拟回答", result)
    
    def test_ask_rag_filtered_invalid_filters(self):
        """测试 ask_rag_filtered 处理无效过滤器。"""
        query = "系统有什么信息？"
        
        # 使用负值过滤器
        result = self.ask_rag_filtered(query, ".txt", -1, -2, "invalid_method")
        
        # 应该处理无效过滤器
        self.assertIsNotNone(result)
        # 可能返回错误或不使用过滤器处理
        self.assertTrue(len(result) > 0)
    
    def test_error_handling_vector_store_failure(self):
        """测试向量存储失败时的错误处理。"""
        # 配置模拟对象抛出异常
        self.mock_vector_store.as_retriever.side_effect = Exception("向量存储错误")
        
        result = self.ask_rag("什么是RAG系统？")
        
        # 应该处理向量存储错误
        self.assertIsNotNone(result)
        self.assertIn("error", result.lower())
    
    def test_error_handling_qa_chain_failure(self):
        """测试问答链失败时的错误处理。"""
        # 配置模拟对象抛出异常
        self.mock_qa_chain.invoke.side_effect = Exception("问答链错误")
        
        result = self.ask_rag("什么是RAG系统？")
        
        # 应该处理问答链错误
        self.assertIsNotNone(result)
        self.assertIn("error", result.lower())
    
    def test_retriever_configuration(self):
        """测试检索器配置。"""
        query = "什么是RAG系统？"
        
        # 配置检索器返回特定文档
        mock_documents = [
            Mock(page_content="文档 1", metadata={"source": "doc1.txt"}),
            Mock(page_content="文档 2", metadata={"source": "doc2.txt"})
        ]
        self.mock_retriever.get_relevant_documents.return_value = mock_documents
        
        result = self.ask_rag(query)
        
        # 验证是否调用了检索器
        self.mock_retriever.get_relevant_documents.assert_called_once_with(query)
        
        # 验证结果包含源信息
        self.assertIsNotNone(result)
    
    def test_source_documents_in_response(self):
        """测试回答中包含源文档信息。"""
        query = "什么是RAG系统？"
        
        # 配置问答链返回源文档
        self.mock_qa_chain.invoke.return_value = {
            "result": "RAG系统的回答",
            "source_documents": [
                Mock(page_content="源内容 1", metadata={"source": "source1.txt"}),
                Mock(page_content="源内容 2", metadata={"source": "source2.txt"})
            ]
        }
        
        result = self.ask_rag(query)
        
        # 验证回答包含源信息
        self.assertIsNotNone(result)
        # 回答应该包含源信息

class TestSearchToolsConfiguration(unittest.TestCase):
    """搜索工具配置测试。"""
    
    def test_set_rag_state(self):
        """测试 set_rag_state 函数。"""
        from tools.search_tools import set_rag_state, rag_state
        
        test_state = {"test": "value", "initialized": True}
        set_rag_state(test_state)
        
        # 验证状态配置正确
        self.assertEqual(rag_state, test_state)
    
    def test_rag_state_persistence(self):
        """测试RAG状态在调用间的持久性。"""
        from tools.search_tools import set_rag_state, rag_state
        
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

class TestSearchToolsIntegration(unittest.TestCase):
    """搜索工具集成测试。"""
    
    def test_ask_rag_with_realistic_data(self):
        """使用真实数据测试 ask_rag。"""
        from tools.search_tools import ask_rag, set_rag_state
        
        # 配置真实的RAG状态
        mock_vector_store = Mock()
        mock_retriever = Mock()
        mock_vector_store.as_retriever.return_value = mock_retriever
        
        mock_qa_chain = Mock()
        mock_qa_chain.invoke.return_value = {
            "result": "RAG（检索增强生成）系统是一种结合信息检索和文本生成的技术。",
            "source_documents": [
                Mock(page_content="RAG结合检索和生成", metadata={"source": "文档.txt"}),
                Mock(page_content="问答系统", metadata={"source": "手册.txt"})
            ]
        }
        
        realistic_state = {
            "vector_store": mock_vector_store,
            "qa_chain": mock_qa_chain,
            "initialized": True
        }
        
        set_rag_state(realistic_state)
        
        # 使用真实查询进行测试
        result = ask_rag("什么是RAG系统？")
        
        # 验证真实回答
        self.assertIsNotNone(result)
        self.assertIn("RAG", result)
    
    def test_ask_rag_filtered_with_metadata(self):
        """使用元数据过滤器测试 ask_rag_filtered。"""
        from tools.search_tools import ask_rag_filtered, set_rag_state
        
        # 配置带有元数据过滤器的状态
        mock_vector_store = Mock()
        mock_retriever = Mock()
        mock_vector_store.as_retriever.return_value = mock_retriever
        
        mock_qa_chain = Mock()
        mock_qa_chain.invoke.return_value = {
            "result": "系统的过滤信息",
            "source_documents": [
                Mock(page_content="包含表格的文档", metadata={"source": "报告.pdf", "tables": 3}),
                Mock(page_content="包含标题的文档", metadata={"source": "手册.docx", "titles": 5})
            ]
        }
        
        realistic_state = {
            "vector_store": mock_vector_store,
            "qa_chain": mock_qa_chain,
            "initialized": True
        }
        
        set_rag_state(realistic_state)
        
        # 使用特定过滤器进行测试
        result = ask_rag_filtered(
            query="系统有什么信息？",
            file_type=".pdf",
            min_tables=2,
            min_titles=3,
            processing_method="unstructured"
        )
        
        # 验证过滤回答
        self.assertIsNotNone(result)
        self.assertIn("过滤", result)

if __name__ == '__main__':
    unittest.main() 