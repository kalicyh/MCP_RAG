# pre_download_model.py
import sys
from sentence_transformers import SentenceTransformer
# 导入 Rich 以增强控制台输出
from rich import print as rich_print
from rich.panel import Panel

def log(message: str):
    """使用 Rich 在控制台中打印消息。"""
    if any(word in message.lower() for word in ["error", "falló", "fatal", "excepción"]):
        rich_print(Panel(f"{message}", title="[red]错误[/red]", style="bold red"))
    elif any(word in message.lower() for word in ["éxito", "exitosamente", "completado", "ok"]):
        rich_print(f"[bold green]{message}[/bold green]")
    else:
        rich_print(message)

# 系统使用的嵌入模型
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

def download_embedding_model():
    """
    下载并缓存 HuggingFace 的嵌入模型。
    这对于首次运行很有用，以便用户可以看到进度。
    """
    log(f"开始下载嵌入模型: {EMBEDDING_MODEL_NAME}")
    log("这可能需要几分钟，具体取决于您的网络连接。")
    log("下载将保存在 HuggingFace 的缓存中，以供将来使用。")
    log("-" * 60)

    try:
        # 实例化 SentenceTransformer 时，会下载并缓存模型。
        # 下载进度应自动显示在控制台中。
        SentenceTransformer(EMBEDDING_MODEL_NAME, device='cpu')
        
        log("-" * 60)
        log("✅ 嵌入模型已成功下载并缓存！")
        log("现在 RAG 服务器的启动速度会更快。")

    except Exception as e:
        log(f"\n❌ 下载模型时出错: {e}")
        log("请检查您的网络连接并重试。")
        log("如果问题仍然存在，可能是 HuggingFace 服务器或防火墙的问题。")

if __name__ == "__main__":
    download_embedding_model()