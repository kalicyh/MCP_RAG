#!/usr/bin/env python3
"""
简单的 Web 界面用于测试 MCP RAG 工具
使用 Flask 提供 Web 界面，让用户可以交互式地测试各种工具
"""

import sys
import inspect
from flask import Flask, render_template_string, request, jsonify
import json

# 导入 server 以初始化 mcp
try:
    import mcp_rag.server as server
    mcp = server.mcp
    print("Loaded server and mcp successfully.")
except Exception as e:
    print(f"Error importing server: {e}")
    sys.exit(2)

# 导入工具列表
try:
    import mcp_rag.tools as tools_module
    ALL_TOOLS = tools_module.ALL_TOOLS
except Exception as e:
    print(f"Error importing ALL_TOOLS from tools: {e}")
    ALL_TOOLS = []

# 构建要测试的工具名列表
tool_names = [fn.__name__ for fn in ALL_TOOLS]
if not tool_names:
    tool_names = [name for name in dir(mcp) if not name.startswith('_')]

# 已知可能有副作用的工具
MUTATING_TOOLS = {
    'learn_text', 'learn_document', 'learn_from_url',
    'clear_embedding_cache_tool', 'optimize_vector_database', 'reindex_vector_database'
}

# 工具中文说明
TOOL_CHINESE = {
    'learn_text': '添加文本到知识库（手动输入）',
    'learn_document': '处理并添加本地文档到知识库（文件路径）',
    'ask_rag': '基于知识库回答问题（返回简洁回答）',
    'ask_rag_filtered': '带过滤器的知识库查询（按元数据筛选）',
    'get_knowledge_base_stats': '显示知识库文档和处理方法的统计信息',
    'get_embedding_cache_stats': '显示嵌入缓存命中/未命中统计',
    'get_data_paths': '查看存储路径信息',
    'clear_embedding_cache_tool': '清理嵌入缓存（删除磁盘/内存缓存）',
    'optimize_vector_database': '优化向量数据库以提高搜索性能',
    'get_vector_database_stats': '显示向量数据库统计信息（集合、维度等）',
    'reindex_vector_database': '重新索引向量数据库（可能耗时）',
}

app = Flask(__name__)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size

# 确保上传目录存在
import os
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# HTML 模板
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MCP RAG 工具测试</title>
    <style>
        :root {
          --bg-color: #edf1f8;
          --card-bg: rgba(255, 255, 255, 0.9);
          --text-primary: #1a1a1a;
          --text-secondary: #666;
          --accent-blue: #007acc;
          --accent-orange: #ff6b35;
          --accent-purple: #8b5cf6;
          --shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
          --border-radius: 20px;
          --font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "PingFang SC", sans-serif;
        }

        * {
          box-sizing: border-box;
          margin: 0;
          padding: 0;
        }

        body {
          background: var(--bg-color);
          font-family: var(--font-family);
          color: var(--text-primary);
          line-height: 1.6;
          min-height: 100vh;
        }

        main {
          max-width: 1400px;
          margin: 0 auto;
          padding: clamp(1rem, 4vw, 2rem);
        }

        .grid {
          display: grid;
          grid-template-columns: repeat(12, minmax(0, 1fr));
          gap: clamp(1rem, 2vw, 1.5rem);
        }

        .card {
          background: var(--card-bg);
          backdrop-filter: blur(10px);
          border: 1px solid rgba(255, 255, 255, 0.2);
          border-radius: var(--border-radius);
          box-shadow: var(--shadow);
          padding: clamp(1.5rem, 3vw, 2rem);
          transition: all 0.3s ease;
          overflow: hidden;
        }

        .card:hover {
          transform: translateY(-2px);
          box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
        }

        .hero {
          grid-column: span 12;
          text-align: center;
          background: linear-gradient(135deg, var(--accent-blue), var(--accent-purple));
          color: white;
          position: relative;
        }

        .hero::before {
          content: '';
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="20" cy="20" r="2" fill="rgba(255,255,255,0.1)"/><circle cx="80" cy="80" r="2" fill="rgba(255,255,255,0.1)"/><circle cx="40" cy="60" r="1" fill="rgba(255,255,255,0.1)"/></svg>');
          opacity: 0.1;
        }

        .hero-badge {
          display: inline-block;
          background: rgba(255, 255, 255, 0.2);
          color: white;
          padding: 0.5rem 1rem;
          border-radius: 50px;
          font-size: clamp(0.8rem, 2vw, 0.9rem);
          font-weight: 600;
          text-transform: uppercase;
          letter-spacing: 0.05em;
          margin-bottom: 1rem;
        }

        .hero-title {
          font-size: clamp(2rem, 5vw, 3rem);
          font-weight: 700;
          margin-bottom: 1rem;
          line-height: 1.2;
        }

        .hero-subtitle {
          font-size: clamp(1rem, 2.5vw, 1.2rem);
          opacity: 0.9;
          margin-bottom: 1.5rem;
          max-width: 600px;
          margin-left: auto;
          margin-right: auto;
        }

        .hero-meta {
          display: flex;
          justify-content: center;
          gap: 1rem;
          flex-wrap: wrap;
        }

        .meta-pill {
          background: rgba(255, 255, 255, 0.15);
          color: white;
          padding: 0.5rem 1rem;
          border-radius: 50px;
          font-size: 0.9rem;
          font-weight: 500;
        }

        .section-title {
          font-size: clamp(1.5rem, 3vw, 2rem);
          font-weight: 600;
          margin-bottom: 1rem;
          color: var(--text-primary);
        }

        .section-desc {
          color: var(--text-secondary);
          margin-bottom: 1.5rem;
          font-size: clamp(0.9rem, 2vw, 1rem);
        }

        .tool-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
          gap: 1rem;
        }

        .tool-card {
          background: rgba(255, 255, 255, 0.8);
          border: 1px solid rgba(0, 0, 0, 0.05);
          border-radius: 16px;
          padding: 1.5rem;
          transition: all 0.3s ease;
          cursor: pointer;
        }

        .tool-card:hover {
          transform: translateY(-2px);
          box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
        }

        .tool-icon {
          width: 48px;
          height: 48px;
          border-radius: 12px;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 1.5rem;
          margin-bottom: 1rem;
        }

        .tool-badge {
          display: inline-block;
          background: var(--accent-blue);
          color: white;
          padding: 0.25rem 0.75rem;
          border-radius: 50px;
          font-size: 0.75rem;
          font-weight: 600;
          text-transform: lowercase;
          margin-bottom: 0.5rem;
        }

        .tool-title {
          font-size: 1.1rem;
          font-weight: 600;
          margin-bottom: 0.5rem;
          color: var(--text-primary);
        }

        .tool-desc {
          color: var(--text-secondary);
          font-size: 0.9rem;
          margin-bottom: 1rem;
        }

        .tool-params {
          margin-top: 1rem;
        }

        .param-input {
          width: 100%;
          padding: 0.5rem;
          border: 1px solid #ddd;
          border-radius: 8px;
          font-family: inherit;
          font-size: 0.9rem;
          margin-bottom: 0.5rem;
        }

        .run-btn {
          background: var(--accent-blue);
          color: white;
          border: none;
          padding: 0.75rem 1.5rem;
          border-radius: 8px;
          cursor: pointer;
          font-size: 0.9rem;
          font-weight: 600;
          width: 100%;
          transition: background 0.3s ease;
        }

        .run-btn:hover {
          background: #005aa3;
        }

        .run-btn.mutating {
          background: var(--accent-orange);
        }

        .run-btn.mutating:hover {
          background: #e55a2b;
        }

        .loading, .status, .output-area {
          margin-top: 1rem;
          display: none;
        }

        .loading {
          text-align: center;
          color: var(--text-secondary);
        }

        .status {
          padding: 0.75rem;
          border-radius: 8px;
          font-size: 0.9rem;
          font-weight: 500;
        }

        .status.success {
          background: #d4edda;
          color: #155724;
          border: 1px solid #c3e6cb;
        }

        .status.error {
          background: #f8d7da;
          color: #721c24;
          border: 1px solid #f5c6cb;
        }

        .output-area {
          background: #f8f9fa;
          border: 1px solid #dee2e6;
          border-radius: 8px;
          padding: 1rem;
        }

        .output-title {
          font-weight: 600;
          margin-bottom: 0.5rem;
          color: var(--text-primary);
        }

        .output-content {
          background: white;
          padding: 0.75rem;
          border-radius: 4px;
          border: 1px solid #ddd;
          font-family: 'Courier New', monospace;
          font-size: 0.85rem;
          white-space: pre-wrap;
          max-height: 300px;
          overflow-y: auto;
        }

        @media (max-width: 1024px) {
          .grid {
            grid-template-columns: 1fr;
          }
          .card {
            grid-column: span 1 !important;
          }
        }
    </style>
</head>
<body>
  <main>
    <div class="grid">
      <!-- Hero Section -->
      <article class="card hero">
        <div class="hero-badge">MCP RAG</div>
        <h1 class="hero-title">智能知识库工具集</h1>
        <p class="hero-subtitle">
          基于大语言模型的检索增强生成系统，提供文档处理、知识问答、统计分析等全方位功能
        </p>
        <div class="hero-meta">
          <span class="meta-pill">🧠 AI 驱动</span>
          <span class="meta-pill">📚 知识库</span>
          <span class="meta-pill">🔍 智能检索</span>
          <span class="meta-pill">📊 数据分析</span>
        </div>
      </article>

      <!-- 添加工具组 -->
      <section class="card" style="grid-column: span 7;">
        <h2 class="section-title">📥 添加内容</h2>
        <p class="section-desc">向知识库添加新的文本或文档内容</p>
        <div class="tool-grid">
          <div class="tool-card" onclick="showTool('learn_text')">
            <div class="tool-icon" style="background: linear-gradient(135deg, var(--accent-blue), #4facfe);">📝</div>
            <span class="tool-badge">文本</span>
            <h3 class="tool-title">添加文本</h3>
            <p class="tool-desc">手动输入文本内容添加到知识库</p>
          </div>
          <div class="tool-card" onclick="showTool('learn_document')">
            <div class="tool-icon" style="background: linear-gradient(135deg, var(--accent-purple), #9c6ade);">📄</div>
            <span class="tool-badge">文档</span>
            <h3 class="tool-title">处理文档</h3>
            <p class="tool-desc">上传并处理文档文件</p>
          </div>
        </div>
      </section>

      <!-- 询问工具组 -->
      <section class="card" style="grid-column: span 5;">
        <h2 class="section-title">❓ 智能问答</h2>
        <p class="section-desc">基于知识库进行智能问答和检索</p>
        <div class="tool-grid">
          <div class="tool-card" onclick="showTool('ask_rag')">
            <div class="tool-icon" style="background: linear-gradient(135deg, #ff9a56, var(--accent-orange));">🤖</div>
            <span class="tool-badge">问答</span>
            <h3 class="tool-title">知识问答</h3>
            <p class="tool-desc">向知识库提问获取答案</p>
          </div>
          <div class="tool-card" onclick="showTool('ask_rag_filtered')">
            <div class="tool-icon" style="background: linear-gradient(135deg, #667eea, #764ba2);">🔍</div>
            <span class="tool-badge">过滤</span>
            <h3 class="tool-title">条件查询</h3>
            <p class="tool-desc">带过滤条件的智能检索</p>
          </div>
        </div>
      </section>

      <!-- 统计工具组 -->
      <section class="card" style="grid-column: span 6;">
        <h2 class="section-title">📊 数据统计</h2>
        <p class="section-desc">查看知识库和系统的统计信息</p>
        <div class="tool-grid">
          <div class="tool-card" onclick="showTool('get_knowledge_base_stats')">
            <div class="tool-icon" style="background: linear-gradient(135deg, #f093fb, #f5576c);">📈</div>
            <span class="tool-badge">知识库</span>
            <h3 class="tool-title">库统计</h3>
            <p class="tool-desc">文档和处理方法统计</p>
          </div>
          <div class="tool-card" onclick="showTool('get_embedding_cache_stats')">
            <div class="tool-icon" style="background: linear-gradient(135deg, #4facfe, #00f2fe);">💾</div>
            <span class="tool-badge">缓存</span>
            <h3 class="tool-title">缓存统计</h3>
            <p class="tool-desc">嵌入缓存性能统计</p>
          </div>
          <div class="tool-card" onclick="showTool('get_vector_database_stats')">
            <div class="tool-icon" style="background: linear-gradient(135deg, #ffecd2, #fcb69f);">📊</div>
            <span class="tool-badge">统计</span>
            <h3 class="tool-title">库统计</h3>
            <p class="tool-desc">向量数据库统计信息</p>
          </div>
        </div>
      </section>

      <!-- 向量库处理工具组 -->
      <section class="card" style="grid-column: span 6;">
        <h2 class="section-title">⚙️ 向量库管理</h2>
        <p class="section-desc">优化和维护向量数据库性能</p>
        <div class="tool-grid">
          <div class="tool-card" onclick="showTool('clear_embedding_cache_tool')">
            <div class="tool-icon" style="background: linear-gradient(135deg, #fa709a, #fee140);">🗑️</div>
            <span class="tool-badge">清理</span>
            <h3 class="tool-title">清理缓存</h3>
            <p class="tool-desc">清除嵌入缓存释放内存</p>
          </div>
          <div class="tool-card" onclick="showTool('optimize_vector_database')">
            <div class="tool-icon" style="background: linear-gradient(135deg, #a8edea, #fed6e3);">🚀</div>
            <span class="tool-badge">优化</span>
            <h3 class="tool-title">优化数据库</h3>
            <p class="tool-desc">提升搜索性能</p>
          </div>
          <div class="tool-card" onclick="showTool('reindex_vector_database')">
            <div class="tool-icon" style="background: linear-gradient(135deg, #ff9a9e, #fecfef);">🔄</div>
            <span class="tool-badge">重建</span>
            <h3 class="tool-title">重建索引</h3>
            <p class="tool-desc">重新索引向量数据库</p>
          </div>
        </div>
      </section>
    </div>

    <!-- 工具详情模态框 -->
    <div id="tool-modal" style="display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 1000; align-items: center; justify-content: center;">
      <div style="background: white; border-radius: 16px; padding: 2rem; max-width: 500px; width: 90%; max-height: 80vh; overflow-y: auto;">
        <h3 id="modal-title" style="margin-bottom: 1rem;"></h3>
        <p id="modal-desc" style="color: var(--text-secondary); margin-bottom: 1.5rem;"></p>
        <div id="modal-params"></div>
        <div style="display: flex; gap: 1rem; margin-top: 1.5rem;">
          <button class="run-btn" id="modal-run-btn" style="flex: 1;">执行</button>
          <button onclick="closeModal()" style="background: #6c757d; color: white; border: none; padding: 0.75rem 1.5rem; border-radius: 8px; cursor: pointer;">关闭</button>
        </div>
        <div class="loading" id="modal-loading">正在执行...</div>
        <div class="status" id="modal-status"></div>
        <div class="output-area" id="modal-output">
          <div class="output-title">执行结果:</div>
          <div class="output-content" id="modal-output-content"></div>
        </div>
      </div>
    </div>
  </main>

    <script>
        const tools = {{ tools_data|tojson }};
        const mutatingTools = {{ mutating_tools|tojson }};

        let currentTool = null;

        function showTool(toolName) {
          const tools = {{ tools_data|tojson }};
          const tool = tools.find(t => t.name === toolName);
          if (!tool) return;

          currentTool = tool;
          document.getElementById('modal-title').textContent = tool.name;
          document.getElementById('modal-desc').textContent = tool.description;

          const paramsContainer = document.getElementById('modal-params');
          paramsContainer.innerHTML = '';

          if (tool.parameters && tool.parameters.length > 0) {
            tool.parameters.forEach(param => {
              const paramDiv = document.createElement('div');
              
              // 特殊处理 learn_document 工具的文件上传
              if (toolName === 'learn_document' && param.name === 'file_path') {
                paramDiv.innerHTML = `
                  <label style="display: block; font-weight: bold; margin-bottom: 0.5rem;">
                    ${param.name} (文件) ${param.required ? '*' : ''}
                  </label>
                  <input type="file" id="modal-param-${param.name}" 
                         accept=".pdf,.docx,.txt,.md,.html,.csv,.json,.xml,.pptx,.xlsx,.odt,.odp,.ods,.rtf,.png,.jpg,.jpeg,.tiff,.bmp,.eml,.msg"
                         style="width: 100%; padding: 0.5rem; border: 1px solid #ddd; border-radius: 8px; font-family: inherit; font-size: 0.9rem;">
                  <small style="color: #666; font-size: 0.8rem;">支持的文件类型: PDF, Word, Excel, PowerPoint, 文本文件, 图片等</small>
                `;
              } else {
                paramDiv.innerHTML = `
                  <label style="display: block; font-weight: bold; margin-bottom: 0.5rem;">
                    ${param.name} (${param.type}) ${param.required ? '*' : ''}
                  </label>
                  <input type="text" class="param-input" id="modal-param-${param.name}"
                         placeholder="${param.default || '输入参数值'}" value="${param.default || ''}">
                `;
              }
              paramsContainer.appendChild(paramDiv);
            });
          }

          const runBtn = document.getElementById('modal-run-btn');
          runBtn.className = tool.is_mutating ? 'run-btn mutating' : 'run-btn';

          document.getElementById('tool-modal').style.display = 'flex';
          document.getElementById('modal-loading').style.display = 'none';
          document.getElementById('modal-status').style.display = 'none';
          document.getElementById('modal-output').style.display = 'none';
        }

        function closeModal() {
          document.getElementById('tool-modal').style.display = 'none';
          currentTool = null;
        }

        document.getElementById('modal-run-btn').addEventListener('click', async () => {
          if (!currentTool) return;

          const loading = document.getElementById('modal-loading');
          const status = document.getElementById('modal-status');
          const outputArea = document.getElementById('modal-output');
          const outputContent = document.getElementById('modal-output-content');

          // 显示加载状态
          loading.style.display = 'block';
          status.style.display = 'none';
          outputArea.style.display = 'none';

          try {
            let response;
            
            // 检查是否是文件上传工具
            if (currentTool.name === 'learn_document') {
              const formData = new FormData();
              formData.append('tool_name', currentTool.name);
              
              // 获取文件输入
              const fileInput = document.getElementById('modal-param-file_path');
              if (fileInput && fileInput.files.length > 0) {
                formData.append('file', fileInput.files[0]);
              } else {
                loading.style.display = 'none';
                status.className = 'status error';
                status.textContent = '请选择要上传的文件';
                status.style.display = 'block';
                return;
              }
              
              response = await fetch('/run_tool', {
                method: 'POST',
                body: formData
              });
            } else {
              // 收集参数
              const args = {};
              if (currentTool.parameters) {
                currentTool.parameters.forEach(param => {
                  const input = document.getElementById(`modal-param-${param.name}`);
                  if (input && input.value.trim()) {
                    args[param.name] = input.value.trim();
                  }
                });
              }

              response = await fetch('/run_tool', {
                method: 'POST',
                headers: {
                  'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                  tool_name: currentTool.name,
                  args: args
                })
              });
            }

            const result = await response.json();

            loading.style.display = 'none';

            if (result.success) {
              status.className = 'status success';
              status.textContent = '执行成功！';
              status.style.display = 'block';

              outputContent.textContent = result.output;
              outputArea.style.display = 'block';
            } else {
              status.className = 'status error';
              status.textContent = `执行失败: ${result.error}`;
              status.style.display = 'block';
            }
          } catch (error) {
            loading.style.display = 'none';
            status.className = 'status error';
            status.textContent = `网络错误: ${error.message}`;
            status.style.display = 'block';
          }
        });

        // 点击模态框背景关闭
        document.getElementById('tool-modal').addEventListener('click', (e) => {
          if (e.target.id === 'tool-modal') {
            closeModal();
          }
        });
    </script>
</body>
</html>
"""

def get_tool_signature(tool_name):
    """获取工具的签名信息"""
    func = None
    if ALL_TOOLS:
        for f in ALL_TOOLS:
            if f.__name__ == tool_name:
                func = f
                break
    else:
        try:
            func = getattr(mcp, tool_name, None)
        except:
            pass

    if not func or not callable(func):
        return {}

    try:
        sig = inspect.signature(func)
        params = []
        for param in sig.parameters.values():
            if param.kind in (param.VAR_POSITIONAL, param.VAR_KEYWORD):
                continue

            param_info = {
                'name': param.name,
                'type': str(param.annotation) if param.annotation != inspect._empty else 'any',
                'default': repr(param.default) if param.default != inspect._empty else None,
                'required': param.default == inspect._empty
            }
            params.append(param_info)

        return {
            'parameters': params,
            'has_required_params': any(p['required'] for p in params)
        }
    except Exception:
        return {}

def build_safe_args(func):
    """为工具构建安全的默认参数"""
    sig = None
    try:
        sig = inspect.signature(func)
    except Exception:
        return []

    call_args = []
    for param in sig.parameters.values():
        if param.kind in (param.VAR_POSITIONAL, param.VAR_KEYWORD):
            continue
        if param.default is not inspect._empty:
            continue
        pname = param.name.lower()
        ann = param.annotation

        if 'text' in pname or 'query' in pname or 'question' in pname or 'url' in pname or 'path' in pname or 'file' in pname or 'source' in pname:
            call_args.append('测试文本')
        elif 'type' in pname or 'method' in pname:
            call_args.append(None)
        elif 'min' in pname or 'count' in pname or 'tables' in pname or 'titles' in pname:
            call_args.append(0)
        elif ann is bool:
            call_args.append(False)
        elif ann in (int, float):
            call_args.append(0)
        else:
            call_args.append(None)
    return call_args

def get_tool_info():
    """获取所有工具的详细信息"""
    tools_data = []
    allowed_tools = set(TOOL_CHINESE.keys())

    # 直接从 ALL_TOOLS 获取工具信息
    if ALL_TOOLS:
        for func in ALL_TOOLS:
            tool_name = func.__name__
            
            # 只包含用户指定的工具
            if tool_name not in allowed_tools:
                continue

            # 获取函数签名
            sig_info = get_tool_signature(tool_name)

            tool_info = {
                'name': tool_name,
                'description': TOOL_CHINESE.get(tool_name, '无描述'),
                'parameters': sig_info.get('parameters', []),
                'is_mutating': tool_name in MUTATING_TOOLS
            }

            tools_data.append(tool_info)
    else:
        # 如果没有 ALL_TOOLS，从 mcp 对象获取（但要小心 session_manager 问题）
        for tool_name in tool_names:
            if tool_name not in allowed_tools:
                continue
                
            sig_info = get_tool_signature(tool_name)

            tool_info = {
                'name': tool_name,
                'description': TOOL_CHINESE.get(tool_name, '无描述'),
                'parameters': sig_info.get('parameters', []),
                'is_mutating': tool_name in MUTATING_TOOLS
            }

            tools_data.append(tool_info)

    return tools_data

@app.route('/upload_file', methods=['POST'])
def upload_file():
    """处理文件上传"""
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': '没有文件部分'})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'error': '没有选择文件'})
    
    if file:
        # 保存文件到上传目录
        filename = file.filename
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        return jsonify({'success': True, 'file_path': file_path})
    
    return jsonify({'success': False, 'error': '文件上传失败'})

@app.route('/')
def index():
    tools_data = get_tool_info()
    return render_template_string(HTML_TEMPLATE,
                               tools_data=tools_data,
                               mutating_tools=list(MUTATING_TOOLS))

@app.route('/run_tool', methods=['POST'])
def run_tool():
    data = request.get_json()
    tool_name = data.get('tool_name')
    args_dict = data.get('args', {})
    
    # 处理文件上传
    if tool_name == 'learn_document' and 'file' in request.files:
        file = request.files['file']
        if file.filename != '':
            # 保存上传的文件
            filename = file.filename
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            args_dict['file_path'] = file_path
    else:
        # 处理普通参数
        for key, value in request.form.items():
            if key != 'tool_name' and value.strip():
                args_dict[key] = value.strip()

    allowed_tools = set(TOOL_CHINESE.keys())
    if not tool_name or tool_name not in allowed_tools:
        return jsonify({'success': False, 'error': '无效的工具名称'})

    # 从工具模块中找到对应的函数
    func = None
    if ALL_TOOLS:
        for f in ALL_TOOLS:
            if f.__name__ == tool_name:
                func = f
                break
    else:
        # 尝试从 mcp 对象获取
        try:
            func = getattr(mcp, tool_name, None)
        except:
            pass

    if not func or not callable(func):
        return jsonify({'success': False, 'error': '工具不可调用'})

    try:
        # 构建参数列表
        sig = inspect.signature(func)
        call_args = []

        for param in sig.parameters.values():
            if param.kind in (param.VAR_POSITIONAL, param.VAR_KEYWORD):
                continue

            param_name = param.name
            if param_name in args_dict and args_dict[param_name]:
                # 尝试转换参数类型
                value = args_dict[param_name]
                if param.annotation == int:
                    call_args.append(int(value))
                elif param.annotation == float:
                    call_args.append(float(value))
                elif param.annotation == bool:
                    call_args.append(value.lower() in ('true', '1', 'yes'))
                else:
                    call_args.append(value)
            elif param.default != inspect._empty:
                call_args.append(param.default)
            else:
                # 对于必需参数，使用默认值
                call_args.append(build_default_value(param))

        print(f"执行工具: {tool_name}({call_args})")
        result = func(*call_args)

        # 格式化输出
        if isinstance(result, str):
            output = result
        else:
            output = json.dumps(result, ensure_ascii=False, indent=2)

        return jsonify({'success': True, 'output': output})

    except Exception as e:
        error_msg = f"{type(e).__name__}: {str(e)}"
        print(f"工具执行错误: {tool_name} - {error_msg}")
        return jsonify({'success': False, 'error': error_msg})

def build_default_value(param):
    """为参数构建默认值"""
    pname = param.name.lower()
    ann = param.annotation

    if 'text' in pname or 'query' in pname or 'question' in pname or 'url' in pname or 'path' in pname or 'file' in pname or 'source' in pname:
        return '测试文本'
    elif 'type' in pname or 'method' in pname:
        return None
    elif 'min' in pname or 'count' in pname or 'tables' in pname or 'titles' in pname:
        return 0
    elif ann is bool:
        return False
    elif ann in (int, float):
        return 0
    else:
        return None

if __name__ == '__main__':
    print("启动 MCP RAG Web 测试界面...")
    print("访问 http://localhost:5000 开始测试")
    app.run(debug=True, host='0.0.0.0', port=5000)