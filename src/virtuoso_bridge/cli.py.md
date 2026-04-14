# CLI 模块

## 功能概述

virtuoso-bridge 的命令行接口，提供 SSH 隧道管理、仿真任务控制等功能。

## CLI 命令

| 命令 | 说明 |
|------|------|
| `init` | 创建 `.env` 模板文件 |
| `start` | 启动 SSH 隧道并部署守护进程 |
| `stop` | 停止 SSH 隧道 |
| `restart` | 重启 SSH 隧道 |
| `status` | 检查隧道和守护进程状态 |
| `license` | 检查 Spectre 许可证可用性 |
| `sim-jobs` | 显示已提交的仿真任务 |
| `sim-cancel <job-id>` | 取消正在运行的仿真任务 |
| `dismiss-dialog` | 查找并关闭阻塞的 Virtuoso GUI 对话框 |

## 通用参数

| 参数 | 说明 |
|------|------|
| `-p, --profile` | 连接配置文件名（读取 `VB_*_<profile>` 环境变量） |

## 使用示例

```bash
# 初始化配置
virtuoso-bridge init

# 启动隧道
virtuoso-bridge start

# 查看状态
virtuoso-bridge status

# 查看仿真任务
virtuoso-bridge sim-jobs

# 取消仿真
virtuoso-bridge sim-cancel a3f2c1d0

# 多配置文件
virtuoso-bridge start -p worker1
virtuoso-bridge status -p worker1
```

## 环境变量

| 变量 | 说明 | 示例 |
|------|------|------|
| `VB_REMOTE_HOST` | SSH 远程主机 | `my-server` |
| `VB_REMOTE_USER` | SSH 用户名 | `username` |
| `VB_REMOTE_PORT` | 远程守护进程端口 | `65081` |
| `VB_LOCAL_PORT` | 本地转发端口 | `65082` |
| `VB_JUMP_HOST` | 跳板机 | `jumphost` |
| `VB_CADENCE_CSHRC` | Cadence 环境配置文件 | `/path/.cshrc` |

多配置文件使用 `VB_REMOTE_HOST_gpu1` 等形式。
