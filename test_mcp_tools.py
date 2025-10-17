#!/usr/bin/env python3
"""
交互式脚本：以菜单方式测试仓库中所有通过 @mcp.tool() 暴露的工具函数（安全优先）

行为说明:
- 导入 `server` 以初始化 RAG 和 mcp 对象。
- 使用 `tools.ALL_TOOLS` 获取可用工具名字，然后在 `server.mcp` 上寻找同名方法并调用。
- 对于需要参数的工具，使用基于参数名与类型的简单启发式填充安全默认值。
- 对于可能产生副作用的工具，会在执行前逐个询问用户确认（Y/n）。

使用示例:
  uv run ./test_mcp_tools.py

这个脚本适合在本地交互调试时使用；它不会接收 --run-mutating 参数，交互确认代替命令行开关。
"""
import sys
import inspect

# 导入 server 以初始化 mcp
try:
    import server
    mcp = server.mcp
    print("Loaded server and mcp successfully.")
except Exception as e:
    print(f"Error importing server: {e}")
    sys.exit(2)

# 导入工具列表
try:
    from tools import ALL_TOOLS
except Exception as e:
    print(f"Error importing ALL_TOOLS from tools: {e}")
    ALL_TOOLS = []

# 构建要测试的工具名列表
tool_names = [fn.__name__ for fn in ALL_TOOLS]
if not tool_names:
    tool_names = [name for name in dir(mcp) if not name.startswith('_')]

# 已知可能有副作用的工具（将询问）
MUTATING_TOOLS = {
    'learn_text', 'learn_document', 'learn_from_url',
    'clear_embedding_cache_tool', 'optimize_vector_database', 'reindex_vector_database'
}

# 记录用户对 mutating 工具的确认（同一会话内记住）
consented_tools = {}

# 工具中文说明（简短）
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
}

# 简单启发式为参数构造安全值
def build_safe_args(func, ask_user: bool = False):
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

        # 当是交互式单项调用时，允许用户输入替代默认文本
        if 'text' in pname or 'query' in pname or 'question' in pname or 'url' in pname or 'path' in pname or 'file' in pname or 'source' in pname:
            if ask_user:
                try:
                    val = input(f"请输入参数 '{param.name}'（回车使用默认 '测试文本'）: ").strip()
                except (EOFError, KeyboardInterrupt):
                    print('\n输入被取消，使用默认值')
                    val = ''
                call_args.append(val if val else '测试文本')
            else:
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

# 安全打印结果，保留换行
def print_result(name, result):
    rtype = type(result).__name__
    if isinstance(result, str):
        max_len = 2000
        display = result if len(result) <= max_len else result[:max_len] + "\n...(truncated)"
        print(f"OK: {name} -> {rtype}:\n{display}\n")
    else:
        print(f"OK: {name} -> {rtype}: {repr(result)[:200]}")

# 交互菜单
def prompt_yes(prompt: str, default: bool = True) -> bool:
    yn = 'Y/n' if default else 'y/N'
    try:
        resp = input(f"{prompt} [{yn}]: ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        print('\nInput cancelled, skipping.')
        return False
    if not resp:
        return default
    return resp in ('y', 'yes')


def run_tool(name, ask_for_args: bool = False):
    func = getattr(mcp, name, None)
    if not callable(func):
        print(f"SKIP (not callable): {name}")
        return ('skipped', 'not callable')

    is_mutating = name in MUTATING_TOOLS
    if is_mutating:
        # 如果此前用户已同意该工具，则不再提示
        if not consented_tools.get(name, False):
            if not prompt_yes(f"工具 '{name}' 可能会修改数据库，要运行吗？"):
                print(f"SKIP (user): {name}")
                return ('skipped', 'user')
            consented_tools[name] = True

    args = build_safe_args(func, ask_user=ask_for_args)
    try:
        print(f"CALL: {name}({', '.join(repr(a) for a in args)})")
        result = func(*args)
        print_result(name, result)
        return ('ok', result)
    except Exception as e:
        print(f"ERR: {name} raised {type(e).__name__}: {e}")
        return ('error', repr(e))


def main_menu():
    while True:
        # 每次循环开始时显示工具列表，确保每次操作后都能看到
        print('\n工具列表:')
        for i, t in enumerate(tool_names, 1):
            flag = '*' if t in MUTATING_TOOLS else ' '
            desc = TOOL_CHINESE.get(t, '')
            if desc:
                print(f" {i:>3}. {t}{flag} — {desc}")
            else:
                print(f" {i:>3}. {t}{flag}")
        print('\n注：带 * 的工具可能有副作用，运行前会提示确认。')

        try:
            choice = input('\n输入工具编号执行，或按 Enter 依次执行全部，输入 q 退出: ').strip()
        except (EOFError, KeyboardInterrupt):
            print('\n退出')
            break

        if not choice:
            # 执行所有（完成后返回菜单而不是退出）
            for name in tool_names:
                run_tool(name)
            # 完成所有后回到菜单以便再次选择
            continue

        if choice.lower() in ('q', 'quit', 'exit'):
            print('退出')
            break

        # 尝试解析为单个索引或逗号分隔列表
        sel = []
        try:
            for part in choice.split(','):
                part = part.strip()
                if not part:
                    continue
                idx = int(part)
                if 1 <= idx <= len(tool_names):
                    sel.append(tool_names[idx-1])
                else:
                    print(f"无效编号: {part}")
        except ValueError:
            print("请输入工具编号或逗号分隔的编号列表，例如：1,3,5")
            continue

        for name in sel:
            # 用户显式选择单项或部分工具，允许交互输入参数
            run_tool(name, ask_for_args=True)


    # 退出前的小结
    print('\n已完成。')


if __name__ == '__main__':
    main_menu()
