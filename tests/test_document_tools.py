#!/usr/bin/env python3
"""
文档处理工具单元测试。
测试 learn_text、learn_document 和 learn_from_url 函数。
"""

import unittest
import tempfile
import os
import sys
from unittest.mock import Mock, patch, MagicMock

# 将 src 目录添加到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

class TestDocumentTools(unittest.TestCase):
    """文档处理工具测试。"""
    
    def setUp(self):
        """每个测试的初始设置。"""
        # 导入要测试的函数
        from tools.document_tools import learn_text, learn_document, learn_from_url
        
        self.learn_text = learn_text
        self.learn_document = learn_document
        self.learn_from_url = learn_from_url
        
        # 设置模拟 RAG 状态
        self.mock_rag_state = {
            "vector_store": Mock(),
            "initialized": True
        }
        
        # 配置设置函数
        from tools.document_tools import set_rag_state, set_md_converter, set_save_processed_copy_func
        
        set_rag_state(self.mock_rag_state)
        
        # MarkItDown 转换器模拟
        self.mock_md_converter = Mock()
        self.mock_md_converter.convert.return_value = "URL处理后的内容"
        set_md_converter(self.mock_md_converter)
        
        # 保存副本函数模拟
        self.mock_save_func = Mock()
        self.mock_save_func.return_value = "处理后副本.md"
        set_save_processed_copy_func(self.mock_save_func)
    
    def test_learn_text_basic(self):
        """测试 learn_text 的基本文本学习功能。"""
        text = "这是RAG系统的测试文本。"
        source = "test_source"
        
        # 配置向量存储模拟
        self.mock_rag_state["vector_store"].add_texts.return_value = ["doc_id_1"]
        
        result = self.learn_text(text, source)
        
        # 验证是否调用了 add_texts
        self.mock_rag_state["vector_store"].add_texts.assert_called_once()
        
        # 验证结果包含成功信息
        self.assertIn("添加", result.lower() or "处理" in result.lower())
    
    def test_learn_text_empty_text(self):
        """测试 learn_text 处理空文本。"""
        result = self.learn_text("", "test_source")
        
        # 应该正确处理空文本
        self.assertIsNotNone(result)
        self.assertIn("error", result.lower() or "空" in result.lower())
    
    def test_learn_text_no_rag_state(self):
        """测试 learn_text 处理未配置的RAG状态。"""
        from tools.document_tools import set_rag_state
        set_rag_state({})  # 空状态
        
        result = self.learn_text("测试文本", "test_source")
        
        # 应该处理未初始化的RAG状态
        self.assertIsNotNone(result)
        self.assertIn("error", result.lower() or "初始化" in result.lower())
    
    def test_learn_document_valid_file(self):
        """测试 learn_document 处理有效文件。"""
        # 创建临时文件
        test_content = """
# 测试文档

这是一个用于验证处理功能的测试文档。

## 第1节
- 要点 1
- 要点 2

## 第2节
用于处理的示例文本。
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(test_content)
            test_file = f.name
        
        try:
            # 配置向量存储模拟
            self.mock_rag_state["vector_store"].add_texts.return_value = ["doc_id_1"]
            
            result = self.learn_document(test_file)
            
            # 验证文件已处理
            self.assertIsNotNone(result)
            self.assertIn("处理", result.lower() or "添加" in result.lower())
            
            # 验证是否调用了保存副本函数
            self.mock_save_func.assert_called_once()
            
        finally:
            # 清理临时文件
            try:
                os.unlink(test_file)
            except:
                pass
    
    def test_learn_document_nonexistent_file(self):
        """测试 learn_document 处理不存在的文件。"""
        result = self.learn_document("不存在的文件.txt")
        
        # 应该处理不存在的文件
        self.assertIsNotNone(result)
        self.assertIn("error", result.lower() or "未找到" in result.lower())
    
    def test_learn_from_url_valid(self):
        """测试 learn_from_url 处理有效URL。"""
        url = "https://httpbin.org/html"
        
        # 配置向量存储模拟
        self.mock_rag_state["vector_store"].add_texts.return_value = ["doc_id_1"]
        
        result = self.learn_from_url(url)
        
        # 验证URL已处理
        self.assertIsNotNone(result)
        self.assertIn("处理", result.lower() or "添加" in result.lower())
        
        # 验证是否调用了 MarkItDown 转换器
        self.mock_md_converter.convert.assert_called_once_with(url)
        
        # 验证是否调用了保存副本函数
        self.mock_save_func.assert_called_once()
    
    def test_learn_from_url_invalid(self):
        """测试 learn_from_url 处理无效URL。"""
        # 配置模拟对象抛出异常
        self.mock_md_converter.convert.side_effect = Exception("连接错误")
        
        result = self.learn_from_url("https://无效网址-12345.com")
        
        # 应该处理无效URL
        self.assertIsNotNone(result)
        self.assertIn("error", result.lower() or "无法" in result.lower())
    
    def test_error_handling_vector_store_failure(self):
        """测试向量存储失败时的错误处理。"""
        # 配置模拟对象抛出异常
        self.mock_rag_state["vector_store"].add_texts.side_effect = Exception("数据库错误")
        
        result = self.learn_text("测试文本", "test_source")
        
        # 应该处理向量存储错误
        self.assertIsNotNone(result)
        self.assertIn("error", result.lower())

class TestDocumentToolsConfiguration(unittest.TestCase):
    """文档工具配置测试。"""
    
    def test_set_rag_state(self):
        """测试 set_rag_state 函数。"""
        from tools.document_tools import set_rag_state, rag_state
        
        test_state = {"test": "value", "initialized": True}
        set_rag_state(test_state)
        
        # 验证状态配置正确
        self.assertEqual(rag_state, test_state)
    
    def test_set_md_converter(self):
        """测试 set_md_converter 函数。"""
        from tools.document_tools import set_md_converter, md_converter
        
        mock_converter = Mock()
        set_md_converter(mock_converter)
        
        # 验证转换器配置正确
        self.assertEqual(md_converter, mock_converter)
    
    def test_set_save_processed_copy_func(self):
        """测试 set_save_processed_copy_func 函数。"""
        from tools.document_tools import set_save_processed_copy_func, save_processed_copy_func
        
        mock_func = Mock()
        set_save_processed_copy_func(mock_func)
        
        # 验证函数配置正确
        self.assertEqual(save_processed_copy_func, mock_func)

if __name__ == '__main__':
    unittest.main() 