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
    'clear_embedding_cache_tool': '清理嵌入缓存（删除磁盘/内存缓存）',
    'optimize_vector_database': '优化向量数据库以提高搜索性能',
    'get_vector_database_stats': '显示向量数据库统计信息（集合、维度等）',
    'reindex_vector_database': '重新索引向量数据库（可能耗时）',
    'get_data_paths': '显示当前数据存储路径信息',
}

app = Flask(__name__)
app.config['SESSION_TYPE'] = 'filesystem'

# HTML 模板
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MCP RAG 工具测试</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1000px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            text-align: center;
            margin-bottom: 30px;
        }
        .tool-section {
            margin-bottom: 30px;
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 20px;
        }
        .tool-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }
        .tool-name {
            font-size: 18px;
            font-weight: bold;
            color: #333;
        }
        .tool-desc {
            color: #666;
            margin-bottom: 15px;
        }
        .param-inputs {
            margin-bottom: 15px;
        }
        .param-group {
            margin-bottom: 10px;
        }
        .param-label {
            display: block;
            font-weight: bold;
            margin-bottom: 5px;
        }
        .param-input {
            width: 100%;
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-family: monospace;
        }
        .run-btn {
            background: #007acc;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
        }
        .run-btn:hover {
            background: #005aa3;
        }
        .run-btn.mutating {
            background: #ff6b6b;
        }
        .run-btn.mutating:hover {
            background: #ff5252;
        }
        .output-area {
            margin-top: 15px;
            padding: 15px;
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 4px;
            display: none;
        }
        .output-header {
            font-weight: bold;
            margin-bottom: 10px;
            color: #333;
        }
        .output-content {
            background: white;
            padding: 10px;
            border-radius: 4px;
            border: 1px solid #ddd;
            white-space: pre-wrap;
            font-family: 'Courier New', monospace;
            max-height: 300px;
            overflow-y: auto;
        }
        .loading {
            display: none;
            text-align: center;
            margin: 20px 0;
        }
        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #007acc;
            border-radius: 50%;
            width: 30px;
            height: 30px;
            animation: spin 1s linear infinite;
            display: inline-block;
            margin-right: 10px;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .status {
            padding: 10px;
            margin: 10px 0;
            border-radius: 4px;
            display: none;
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
    </style>
</head>
<body>
    <div class="container">
        <h1>MCP RAG 工具测试</h1>

        <div id="tools-container">
            <!-- 工具将在这里动态生成 -->
        </div>
    </div>

    <script>
        const tools = {{ tools_data|tojson }};
        const mutatingTools = {{ mutating_tools|tojson }};

        function createToolSections() {
            const container = document.getElementById('tools-container');

            tools.forEach(tool => {
                const section = document.createElement('div');
                section.className = 'tool-section';

                const isMutating = mutatingTools.includes(tool.name);

                let paramsHtml = '';
                if (tool.parameters && tool.parameters.length > 0) {
                    paramsHtml = tool.parameters.map(param => `
                        <div class="param-group">
                            <label class="param-label">${param.name} (${param.type}) ${param.required ? '*' : ''}</label>
                            <input type="text" class="param-input" id="param-${tool.name}-${param.name}"
                                   placeholder="${param.default || '输入参数值'}" value="${param.default || ''}">
                        </div>
                    `).join('');
                }

                section.innerHTML = `
                    <div class="tool-header">
                        <div class="tool-name">${tool.name}</div>
                        <button class="run-btn ${isMutating ? 'mutating' : ''}" onclick="runTool('${tool.name}')">
                            执行
                        </button>
                    </div>
                    <div class="tool-desc">${tool.description || '无描述'}</div>
                    <div class="param-inputs">
                        ${paramsHtml}
                    </div>
                    <div class="loading" id="loading-${tool.name}">
                        <div class="spinner"></div>
                        正在执行...
                    </div>
                    <div class="status" id="status-${tool.name}"></div>
                    <div class="output-area" id="output-${tool.name}">
                        <div class="output-header">执行结果:</div>
                        <div class="output-content" id="output-content-${tool.name}"></div>
                    </div>
                `;

                container.appendChild(section);
            });
        }

        async function runTool(toolName) {
            const loading = document.getElementById(`loading-${toolName}`);
            const status = document.getElementById(`status-${toolName}`);
            const outputArea = document.getElementById(`output-${toolName}`);
            const outputContent = document.getElementById(`output-content-${toolName}`);

            // 收集参数
            const tool = tools.find(t => t.name === toolName);
            const args = {};
            if (tool.parameters) {
                tool.parameters.forEach(param => {
                    const input = document.getElementById(`param-${toolName}-${param.name}`);
                    if (input && input.value.trim()) {
                        args[param.name] = input.value.trim();
                    }
                });
            }

            // 显示加载状态
            loading.style.display = 'block';
            status.style.display = 'none';
            outputArea.style.display = 'none';

            try {
                const response = await fetch('/run_tool', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        tool_name: toolName,
                        args: args
                    })
                });

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
        }

        // 初始化
        createToolSections();
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