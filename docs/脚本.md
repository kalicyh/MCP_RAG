# 批量导入 GUI 的脚本说明

此目录包含为 Bulk Ingest GUI 准备的“组织化脚本”，用于简化安装与运行。

## 📁 脚本结构

### 主脚本

| 脚本 | 作用 | 何时使用 |
|------|------|----------|
| `start.bat` | 主入口（交互式引导） | 优先使用它 |
| `install_requirements.bat` | 安装全部依赖 | 首次或遇到问题时 |
| `run_gui.bat` | 启动应用 | 安装完成后 |

### 诊断脚本

| 脚本 | 作用 | 何时使用 |
|------|------|----------|
| `check_system.bat` | 检查 Python/GPU/CUDA | 安装异常时 |
| `diagnose_venv.bat` | 诊断虚拟环境 | .venv 有问题时 |
| `force_clean_venv.bat` | 强制清理虚拟环境 | 环境损坏时 |

### 专用脚本

| 脚本 | 作用 | 何时使用 |
|------|------|----------|
| `install_pytorch.bat` | 单独安装 PyTorch | 仅在 PyTorch 异常时 |

## 🚀 使用指南

### 首次使用（推荐）

1) 运行主脚本：
```bash
start.bat
```

2) 选择“1”安装依赖

3) 等待安装完成

4) 应用会自动启动

### 日常使用

1) 运行主脚本：
```bash
start.bat
```

2) 选择“1”启动应用

### 出现问题时

问题：虚拟环境损坏
```bash
force_clean_venv.bat
```

问题：缺少依赖
```bash
install_requirements.bat
```

问题：PyTorch 不工作
```bash
install_pytorch.bat
```

问题：不知道哪里有问题
```bash
check_system.bat
```

## 🔧 职责分离

### install_requirements.bat
- ✅ 系统检查（Python/GPU）
- ✅ 清理损坏的虚拟环境
- ✅ 新建虚拟环境
- ✅ 安装 PyTorch（CPU/CUDA 自动选择）
- ✅ 安装所有依赖
- ✅ 安装验证

### run_gui.bat
- ✅ 确认虚拟环境存在
- ✅ 激活虚拟环境
- ✅ 启动应用
- ✅ 运行期错误处理

### start.bat
- ✅ 判断是否需要安装
- ✅ 交互式引导用户
- ✅ 协调其他脚本
- ✅ 区分首次使用与日常运行

## 📋 工作流

```
start.bat
    ↓
是否需要安装？
    ↓
是 → install_requirements.bat → run_gui.bat
    ↓
否 → run_gui.bat
```

## 🛠️ 这种结构的优势

### 面向用户
- ✅ 简单：只需运行 `start.bat`
- ✅ 直观：菜单清晰、选项明了
- ✅ 稳健：自动处理常见错误
- ✅ 灵活：适配多种场景

### 面向开发者
- ✅ 易维护：单一职责脚本
- ✅ 易调试：快速定位问题环节
- ✅ 可扩展：便于新增功能
- ✅ 可复用：脚本可独立调用

## 🚨 常见问题处理

错误：“未找到虚拟环境”
```bash
start.bat
# 选择“1”安装依赖
```

错误：“无法激活虚拟环境”
```bash
force_clean_venv.bat
start.bat
```

错误：“未找到 PyTorch”
```bash
install_pytorch.bat
```

错误：“未找到 Python”
1) 从 https://www.python.org/downloads/ 安装 Python
2) 安装时勾选 “Add Python to PATH”
3) 重启终端
4) 运行 `start.bat`

## 📝 重要说明

- 始终以 `start.bat` 作为入口
- 未完全了解前，不要直接调用子脚本
- 若失败，先用诊断脚本排查
- 需要重装时，在 `start.bat` 里选择“重装依赖”

## 🔄 升级

升级系统：
1) 运行 `start.bat`
2) 选择“重装依赖”
3) 会自动清理并重装全部组件
