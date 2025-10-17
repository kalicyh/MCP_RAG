import argparse
import sys


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    parser = argparse.ArgumentParser(prog="mcp-rag", description="MCP RAG CLI")
    sub = parser.add_subparsers(dest="cmd")

    serve_p = sub.add_parser("serve", help="启动 MCP server")
    serve_p.add_argument("--host", default=None, help="主机地址（如果使用 Web 服务）")
    serve_p.add_argument("--port", default=None, help="端口（如果使用 Web 服务）")

    web_p = sub.add_parser("web", help="启动 Web 测试界面")
    web_p.add_argument("--host", default="127.0.0.1", help="Web 服务器主机地址")
    web_p.add_argument("--port", type=int, default=5000, help="Web 服务器端口")

    args = parser.parse_args(argv)
    if args.cmd == "serve":
        try:
            from mcp_rag import server
        except Exception as e:
            # 尝试把当前工作目录加入 sys.path（方便在仓库根直接运行）
            import os, traceback
            cwd = os.getcwd()
            if cwd not in sys.path:
                sys.path.insert(0, cwd)
            try:
                from mcp_rag import server
            except Exception as e2:
                print("无法导入 server 模块，尝试将当前工作目录加入 sys.path 后仍失败。")
                print("原始错误:", e)
                print("重试错误:", e2)
                print("建议：确保在仓库根运行此命令，或将项目安装为可导入模块（pip install -e .）并激活对应虚拟环境。")
                traceback.print_exc()
                return 2

        if args.host or args.port:
            host = args.host or "127.0.0.1"
            port = int(args.port) if args.port else 8000
            print(f"Starting MCP server on {host}:{port} (mcp.run host/port) ...")
            try:
                server.mcp.run(host=host, port=port)
            except Exception as e:
                print(f"无法以网络模式启动 server: {e}")
                return 3
        else:
            print("Starting MCP server in stdio mode...")
            try:
                server.mcp.run(transport='stdio')
            except Exception as e:
                print(f"启动 stdio 服务器失败: {e}")
                return 3
    elif args.cmd == "web":
        try:
            import mcp_rag.web as web
        except Exception as e:
            print(f"无法导入 web 模块: {e}")
            return 2

        host = args.host
        port = args.port
        print(f"Starting MCP RAG Web interface on {host}:{port}...")
        print(f"Open your browser and visit: http://{host}:{port}")
        try:
            web.app.run(host=host, port=port, debug=False)
        except Exception as e:
            print(f"启动 Web 服务器失败: {e}")
            return 3
    else:
        parser.print_help()

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
