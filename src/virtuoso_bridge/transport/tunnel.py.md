# SSHClient

## 功能概述

管理 SSH 隧道和远程 RAMIC 守护进程部署。提供 localhost:port TCP 端点，将流量隧道到远程守护进程。

## SSHClient 类

### 构造函数参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `remote_host` | `str` | - | 远程主机 |
| `remote_user` | `str \| None` | `None` | 远程用户名 |
| `port` | `int` | `65432` | 远程守护进程端口 |
| `local_port` | `int \| None` | `None` | 本地绑定端口 |
| `jump_host` | `str \| None` | `None` | 跳板机 |
| `jump_user` | `str \| None` | `None` | 跳板机用户名 |
| `timeout` | `int` | `30` | 操作超时 |
| `keep_remote_files` | `bool` | `False` | 保留远程文件 |
| `profile` | `str \| None` | `None` | 配置 profile |

### 工厂方法

| 方法 | 说明 |
|------|------|
| `from_env(profile)` | 从环境变量创建 |

### 核心方法

| 方法 | 说明 |
|------|------|
| `warm(timeout)` | 完整启动：远程设置 + 持久化 shell + 隧道 |
| `stop()` | 停止隧道并清理 |
| `close()` | 关闭连接（不杀死隧道） |
| `ensure_tunnel()` | 确保隧道运行 |
| `ensure_remote_setup()` | 上传守护进程文件到远程 |
| `ensure_local_setup()` | 本地模式设置 |

### 属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `port` | `int` | 本地端口 |
| `remote_host` | `str` | 远程主机 |
| `ssh_runner` | `SSHRunner` | SSH 运行器 |
| `is_tunnel_alive` | `bool` | 隧道是否存活 |
| `setup_path` | `str \| None` | Virtuoso setup.il 路径 |

### 状态管理

| 方法 | 说明 |
|------|------|
| `save_state()` | 保存状态到 `~/.cache/virtuoso_bridge/state_*.json` |
| `read_state(profile)` | 读取状态 |
| `is_running(profile)` | 检查是否运行 |

## 使用示例

```python
from virtuoso_bridge.transport.tunnel import SSHClient

# 创建并启动
ssh = SSHClient.from_env(keep_remote_files=True)
ssh.warm()  # 启动隧道和远程设置

# 获取连接信息
print(f"Local port: {ssh.port}")
print(f"Setup path: {ssh.setup_path}")

# 停止
ssh.stop()
```

## 本地模式

当 `remote_host` 为 `localhost`、`127.0.0.1` 或 `::1` 时，自动使用本地模式，无需 SSH。

```python
ssh = SSHClient(remote_host="localhost", port=65432)
ssh.warm()
# 然后在 Virtuoso CIW 中加载 ssh.setup_path
```
