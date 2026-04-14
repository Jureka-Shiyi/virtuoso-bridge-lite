# Transport 传输层模块

## 功能概述

SSH 传输工具封装，提供 SSH 连接、文件传输、远程命令执行和端口转发隧道。

## 导入

```python
from virtuoso_bridge.transport import (
    SSHRunner,
    RemoteTaskResult,
    RemoteSshEnv,
    run_remote_task,
    remote_ssh_env_from_os,
    default_virtuoso_bridge_dir,
    remote_scratch_root,
    resolve_remote_username,
)
```

## 导出内容

### SSH 运行器

| 导出 | 类型 | 说明 |
|------|------|------|
| `SSHRunner` | 类 | SSH 连接、命令执行、文件传输 |
| `run_remote_task` | 函数 | 执行远程任务（上传→执行→下载） |
| `remote_ssh_env_from_os` | 函数 | 从 OS 环境获取 SSH 环境信息 |
| `RemoteTaskResult` | 类 | 远程任务结果 |
| `RemoteSshEnv` | 类 | SSH 环境信息 |

### 远程路径

| 导出 | 类型 | 说明 |
|------|------|------|
| `default_virtuoso_bridge_dir` | 函数 | 获取默认远程工作目录 |
| `remote_scratch_root` | 函数 | 获取远程 scratch 根目录 |
| `resolve_remote_username` | 函数 | 解析远程用户名 |

## 子模块

| 模块 | 说明 |
|------|------|
| `transport.ssh` | SSHRunner 核心实现 |
| `transport.tunnel` | SSH 隧道管理（端口转发） |
| `transport.remote_paths` | 远程路径解析辅助 |

## 使用示例

### SSH 命令执行

```python
from virtuoso_bridge.transport import SSHRunner

runner = SSHRunner(host="server", user="zhangz")
result = runner.run_command("ls -la /tmp")
print(result.stdout)
```

### 文件传输

```python
from pathlib import Path
from virtuoso_bridge.transport import SSHRunner

runner = SSHRunner(host="server", user="zhangz")

# 上传文件
runner.upload(Path("script.py"), "/tmp/script.py")

# 下载文件
runner.download("/tmp/result.txt", Path("result.txt"))
```

### 端口转发隧道

```python
from virtuoso_bridge.transport import SSHRunner

runner = SSHRunner(host="server", user="zhangz")
runner.start_port_forward(local_port=65082, remote_port=65081)

if runner.is_tunnel_alive:
    print(f"Tunnel PID: {runner.tunnel_pid}")

runner.stop_port_forward()
```
