# Virtuoso Basic 基础连接模块

## 功能概述

Virtuoso 基础连接功能，通过 TCP 与 Virtuoso CIW 中的 RAMIC 守护进程通信来执行 SKILL 代码。

## 导入

```python
from virtuoso_bridge.virtuoso.basic import VirtuosoClient
```

## 导出内容

| 导出 | 类型 | 说明 |
|------|------|------|
| `VirtuosoClient` | 类 | Virtuoso SKILL 执行客户端 |

## VirtuosoClient

### 简介

通过 RAMIC 守护进程在 Virtuoso 中执行 SKILL 代码的 Python 客户端。支持：
- SKILL 代码执行
- 文件上传/下载
- IL 文件加载
- Layout/Schematic 编辑操作
- Maestro (ADE Assembler) 仿真管理

### 工厂方法

| 方法 | 说明 |
|------|------|
| `from_env(timeout, profile)` | 从环境变量创建 |
| `local(host, port, timeout)` | 创建本地模式客户端 |
| `from_tunnel(tunnel, timeout)` | 通过 SSH 隧道创建 |

### 核心方法

| 方法 | 说明 |
|------|------|
| `execute_skill(skill_code, timeout)` | 执行 SKILL 代码 |
| `test_connection(timeout)` | 测试连接 |
| `ensure_ready(timeout)` | 确保就绪 |
| `warm_remote_session(timeout)` | 预热远程会话 |

### 文件操作

| 方法 | 说明 |
|------|------|
| `download_file(remote, local, timeout)` | 下载远程文件 |
| `upload_file(local, remote, timeout)` | 上传本地文件 |
| `load_il(path, timeout)` | 加载 IL 文件 |

### 窗口操作

| 方法 | 说明 |
|------|------|
| `open_window(lib, cell, view, timeout)` | 打开窗口 |
| `open_cell_view(lib, cell, view, mode, timeout)` | 打开 cellview |
| `save_current_cellview(timeout)` | 保存当前 cellview |
| `close_current_cellview(timeout)` | 关闭当前 cellview |
| `get_current_design(timeout)` | 获取当前设计信息 |

## 使用示例

```python
from virtuoso_bridge.virtuoso.basic import VirtuosoClient

# 远程模式（使用 SSH 隧道）
client = VirtuosoClient.from_env()

# 本地模式
client = VirtuosoClient.local(port=65432)

# 执行 SKILL
result = client.execute_skill("1+2")
print(result.output)

# 文件传输
client.upload_file("local.py", "/tmp/remote.py")
client.download_file("/tmp/result.txt", "output.txt")

# 加载 IL 脚本
client.load_il("/path/to/script.il")
```

## 子模块

| 模块 | 说明 |
|------|------|
| `virtuoso.basic.bridge` | VirtuosoClient 完整实现 |
| `virtuoso.basic.composition` | SKILL 脚本组合工具 |
| `virtuoso.basic.resources` | RAMIC 守护进程资源文件 |
