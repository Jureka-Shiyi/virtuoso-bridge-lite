# VirtuosoClient

## 功能概述

通过 RAMIC 守护进程在 Virtuoso 中执行 SKILL 代码的 Python 客户端。

## VirtuosoClient 类

### 构造函数参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `host` | `str` | `"127.0.0.1"` | 守护进程主机 |
| `port` | `int` | `65432` | 守护进程端口 |
| `timeout` | `int` | `30` | 默认超时 |
| `tunnel` | `Any` | `None` | SSHClient 实例 |
| `log_to_ciw` | `bool` | `True` | 是否在 CIW 打印日志 |

### 工厂方法

| 方法 | 说明 |
|------|------|
| `from_env(timeout, profile)` | 从环境变量创建 |
| `local(host, port, timeout)` | 创建本地模式客户端 |
| `from_tunnel(tunnel, timeout)` | 通过隧道创建 |

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

### 其他操作

| 方法 | 说明 |
|------|------|
| `ciw_print(message, timeout)` | 在 CIW 打印消息 |
| `ciw_log(skill_code, timeout)` | 执行 SKILL 并记录 |
| `run_shell_command(cmd, timeout)` | 执行 shell 命令 |
| `dismiss_dialog(display)` | 关闭阻塞对话框 |

### 子模块

| 属性 | 类型 | 说明 |
|------|------|------|
| `layout` | `LayoutOps` | Layout 编辑操作 |
| `schematic` | `SchematicOps` | Schematic 编辑操作 |

## 使用示例

```python
from virtuoso_bridge import VirtuosoClient

# 远程模式
client = VirtuosoClient.from_env()

# 本地模式
client = VirtuosoClient.local(port=65432)

# 执行 SKILL
result = client.execute_skill("1+2")
print(result.output)

# 文件传输
client.upload_file("local.py", "/tmp/remote.py")
client.download_file("/tmp/result.txt", "output.txt")

# 加载 IL
client.load_il("/path/to/script.il")
```

## 上下文管理器

```python
with VirtuosoClient.from_env() as client:
    result = client.execute_skill("1+2")
    # 自动关闭
```

## IL 上传缓存

`load_il()` 通过 MD5 哈希缓存已上传文件，避免重复上传。
