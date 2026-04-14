# SSH 运行器

## 功能概述

通过 OpenSSH CLI 工具执行远程命令，支持文件上传下载、端口转发隧道。

## SSHRunner 类

### 构造函数参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `host` | `str` | - | SSH 目标主机 |
| `user` | `str \| None` | `None` | SSH 用户名 |
| `jump_host` | `str \| None` | `None` | 跳板机 |
| `jump_user` | `str \| None` | `None` | 跳板机用户名 |
| `ssh_key_path` | `Path \| None` | `None` | SSH 密钥路径 |
| `timeout` | `int` | `600` | 命令超时 |
| `connect_timeout` | `int` | `30` | 连接超时 |
| `persistent_shell` | `bool` | `False` | 是否使用持久化 shell |
| `verbose` | `bool` | `False` | 详细输出 |

### 核心方法

| 方法 | 说明 |
|------|------|
| `test_connection(timeout)` | 测试 SSH 连接 |
| `run_command(command, timeout)` | 执行远程命令 |
| `upload(local_path, remote_path)` | 上传文件/目录 |
| `upload_batch(files)` | 批量上传多个文件 |
| `upload_text(text, remote_path)` | 上传文本内容 |
| `download(remote_path, local_path)` | 下载文件/目录 |
| `start_port_forward(port, remote_port)` | 启动端口转发隧道 |
| `stop_port_forward()` | 停止端口转发隧道 |
| `ensure_persistent_shell()` | 确保持久化 shell 启动 |
| `close()` | 关闭连接 |

### 端口转发

```python
# 启动隧道
runner.start_port_forward(local_port=65082, remote_port=65081)

# 检查状态
if runner.is_tunnel_alive:
    print(f"Tunnel PID: {runner.tunnel_pid}")

# 停止隧道
runner.stop_port_forward()
```

### 文件传输

```python
# 上传文件
runner.upload(Path("local.py"), "/tmp/remote.py")

# 批量上传
runner.upload_batch([
    (Path("file1.py"), "/tmp/file1.py"),
    (Path("file2.py"), "/tmp/file2.py"),
])

# 上传文本
runner.upload_text("hello world", "/tmp/test.txt")

# 下载
runner.download("/tmp/remote.txt", Path("local.txt"))
```

## 远程任务执行

### `run_remote_task()`

执行远程任务：上传文件 → 执行命令。

```python
from virtuoso_bridge.transport.ssh import run_remote_task, SSHRunner

runner = SSHRunner(host="server", user="user")
result = run_remote_task(
    runner,
    work_dir_base="/tmp",
    run_id="task1",
    uploads=[(Path("script.py"), "/tmp/script.py")],
    command="python /tmp/script.py",
    timeout=300,
)
```

## 命令日志

所有 SSH/SCP 命令记录到 `logs/commands.log`。

## ControlMaster

Linux/macOS 自动启用 SSH ControlMaster 连接复用，Windows 不支持。
