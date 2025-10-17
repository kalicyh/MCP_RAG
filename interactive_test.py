#!/usr/bin/env python3
"""
MCP 服务器交互式测试
=================================

此脚本允许从编辑器交互式测试 MCP 服务器的工具。
"""

import sys
import os

# 将 src 目录添加到路径
sys.path.insert(0, 'src')

def interactive_test():
    """MCP 服务器的交互式测试。"""
    
    print("🚀 **MCP 服务器交互式测试**")
    print("=" * 50)
    
    try:
        # 导入服务器
        from server import mcp
        print("✅ MCP 服务器加载成功")
        
        while True:
            print("\n" + "="*50)
            print("可用选项:")
            print("1. 添加文本 (learn_text)")
            print("2. 查看统计信息 (get_knowledge_base_stats)")
            print("3. 提问 (ask_rag)")
            print("4. 查看嵌入缓存 (get_embedding_cache_stats)")
            print("5. 清理缓存 (clear_embedding_cache_tool)")
            print("6. 退出")
            print("="*50)
            
            choice = input("\n请选择一个选项 (1-6): ").strip()
            
            if choice == "1":
                text = input("请输入要添加的文本: ")
                result = mcp.learn_text(text)
                print(f"\n结果: {result}")
                
            elif choice == "2":
                stats = mcp.get_knowledge_base_stats()
                print(f"\n统计信息:\n{stats}")
                
            elif choice == "3":
                question = input("请输入您的问题: ")
                answer = mcp.ask_rag(question)
                print(f"\n回答:\n{answer}")
                
            elif choice == "4":
                cache_stats = mcp.get_embedding_cache_stats()
                print(f"\n缓存统计信息:\n{cache_stats}")
                
            elif choice == "5":
                result = mcp.clear_embedding_cache_tool()
                print(f"\n结果: {result}")
                
            elif choice == "6":
                print("👋 再见！")
                break
                
            else:
                print("❌ 无效选项。请重试。")
                
    except Exception as e:
        print(f"❌ 错误: {e}")

if __name__ == "__main__":
    interactive_test()