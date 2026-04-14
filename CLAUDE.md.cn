# CLAUDE.md

本文件为在此代码库工作时向 Claude Code (claude.ai/code) 提供指导。

## 项目概述

**virtuoso-bridge-lite** 是一个 Python bridge，用于通过 SSH 隧道远程控制 Cadence Virtuoso。它使 LLM agents 能够跨 schematic 编辑、layout 生成、Maestro 仿真设置和独立 Spectre 仿真自动化模拟/混合信号设计任务。

关键架构决策：
- **基于字符串的 SKILL 执行**（与 skillbridge 不同，不是 Pythonic 对象映射）
- **SSH 优先设计**，具有自动隧道管理和跳板机支持
- **基于上下文管理器的编辑 API** 用于 layout/schematic（`with client.layout.edit() as layout:`）
- **AI 原生 CLI**（`virtuoso-bridge start/status/restart`），skill 文件位于 `skills/`

## 常见开发命令

### 安装

```bash
# 创建虚拟环境并安装（使用 uv，不要用全局 Python）
uv venv .venv && source .venv/bin/activate  # Windows: source .venv/Scripts/activate
uv pip install -e ".[dev]"

# 初始化配置
virtuoso-bridge init  # 创建 .env 模板
```

### 测试

```bash
# 运行所有测试
pytest

# 运行单个测试文件
pytest tests/test_bridge.py

# 详细输出
pytest -v
```

### CLI 使用（开发时）

```bash
# 启动/停止/重启 SSH 隧道
virtuoso-bridge start
virtuoso-bridge status  # 显示隧道 + 守护进程 + Spectre 状态
virtuoso-bridge restart
virtuoso-bridge stop

# 多 Profile（连接多台服务器）
virtuoso-bridge start -p worker1
virtuoso-bridge status -p worker1

# Spectre 仿真管理
virtuoso-bridge license          # 检查 Spectre license
virtuoso-bridge sim-jobs         # 列出运行中的仿真
virtuoso-bridge sim-cancel <id>  # 取消作业

# X11 对话框恢复（当 SKILL 通道被阻塞时）
virtuoso-bridge dismiss-dialog
```

### 环境变量（.env 文件）

```bash
VB_REMOTE_HOST=my-server        # ~/.ssh/config 中的 SSH 主机别名
VB_REMOTE_USER=username         # SSH 用户名
VB_REMOTE_PORT=65081            # 远程守护进程端口
VB_LOCAL_PORT=65082             # 本地转发端口
VB_JUMP_HOST=jump-host          # 可选的堡垒机/跳板机
VB_CADENCE_CSHRC=/path/.cshrc   # 用于 Spectre PATH 设置
```

多 Profile 设置：追加 profile 后缀：`VB_REMOTE_HOST_worker1`、`VB_REMOTE_USER_worker1` 等。

## 高层架构

### 三层设计

```
┌─────────────────────────────────────────────────────────────┐
│  应用层                                                       │
│  ├── VirtuosoClient (SKILL 执行)                             │
│  ├── LayoutOps / SchematicOps (上下文管理器)                  │
│  ├── Maestro 会话 (read_config, write, run_sim)              │
│  └── SpectreSimulator (独立仿真)                              │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│  传输层 (SSHClient)                                           │
│  ├── 带 ControlMaster 的 SSH 隧道（持久连接）                  │
│  ├── 端口转发 (-L local:remote)                              │
│  ├── 文件传输（通过 SSHRunner 的 rsync/scp）                  │
│  └── 远程命令执行                                            │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│  守护进程层（远程主机上）                                      │
│  ├── ramic_daemon.py (TCP 服务器，将 SKILL 中继到 stdout)    │
│  └── Virtuoso CIW（加载了 ramic_bridge.il）                 │
└─────────────────────────────────────────────────────────────┘
```

### 两种运行模式

**远程模式**（生产环境）：
- SSH 隧道通过 `virtuoso-bridge start` 自动建立
- 守护进程部署到远程，在 Virtuoso CIW 中加载
- 所有流量通过加密隧道

**本地模式**（开发/测试）：
- 无 SSH，无需 .env
- 直接在本地 Virtuoso 中加载 `core/ramic_bridge.il`
- `VirtuosoClient.local(port=65432)`

### SKILL Bridge 协议

Python 和 Virtuoso 之间的通信协议使用定界消息：

```
请求（JSON over TCP）:  {"skill": "1+2", "timeout": 30}

响应格式:
  成功: \x02<result>\x1e
  错误: \x15<error_message>\x1e
```

标记：`\x02`（STX = 成功），`\x15`（NAK = 错误），`\x1e`（RS = 记录结束）

守护进程（`ramic_daemon.py`）接收 TCP，将 SKILL 写入 stdout（Virtuoso 的 IPC），从 stdin 读取结果，通过 TCP 返回。

## 关键代码模式

### VirtuosoClient 使用模式

```python
from virtuoso_bridge import VirtuosoClient

# 远程模式（使用 .env 中的 SSH 隧道）
client = VirtuosoClient.from_env()

# 本地模式
client = VirtuosoClient.local(port=65432)

# 执行原始 SKILL
result = client.execute_skill("1+2")  # 返回 VirtuosoResult，包含 status/output/errors

# 文件操作
client.upload_file("local.py", "/tmp/remote.py")
client.download_file("/tmp/remote.raw", "local.raw")

# 加载 IL 文件（远程时自动上传）
client.load_il("my_script.il")
```

### Layout 编辑上下文管理器

```python
# 模式：打开 cellview → 排队操作 → 成功时自动保存
with client.layout.edit("myLib", "myCell", mode="w") as layout:
    layout.add(layout_create_rect("M1", "drawing", 0, 0, 10, 10))
    layout.add(layout_create_inst("tsmcN28", "nch_mac", "M0", 0, 0))
# 自动：成功时 dbSave()，异常时回滚
```

### Schematic 编辑

```python
with client.schematic.edit("myLib", "inv") as sch:
    sch.add(schematic_create_inst_by_master_name("tsmcN28", "pch_mac", "MP0", 0, 1.5, "R0"))
    # 使用 add_net_label_to_transistor() 进行 MOS 布线，不要用手动 add_wire
    sch.add_net_label_to_transistor("MP0", drain_net="OUT", gate_net="IN", source_net="VDD")
```

### Maestro 仿真工作流

```python
from virtuoso_bridge.virtuoso.maestro import open_session, read_config, close_session

session = open_session(client, "myLib", "myTestbench")  # maeOpenSetup（后台）
config = read_config(client, session)  # 包含 tests、analyses、variables 的字典

# 设置变量并运行
client.execute_skill(f'maeSetVar("VDD" "0.8" ?session "{session}")')
client.execute_skill(f'maeSaveSetup(... ?session "{session}")')
history = client.execute_skill(f'maeRunSimulation(?session "{session}")').output
client.execute_skill("maeWaitUntilDone('All)", timeout=300)

close_session(client, session)
```

### Spectre 独立仿真

```python
from virtuoso_bridge.spectre import SpectreSimulator, spectre_mode_args

sim = SpectreSimulator.from_env(
    spectre_args=spectre_mode_args("ax"),  # APS 扩展模式
    work_dir="./output"
)

# 运行仿真
result = sim.run_simulation("netlist.scs", {"include_files": ["model.va"]})
if result.ok:
    vout = result.data["VOUT"]  # 解析后的 PSF 波形为 float 列表

# 并行批处理
from pathlib import Path
tasks = [sim.submit(Path(f"tb_{i}.scs")) for i in range(10)]
results = [t.result() for t in tasks]
```

## 重要实现细节

### 跳板机连接重试
Bridge 实现了通过跳板机连接的专门重试逻辑（参见 `_TUNNEL_CONNECT_GRACE_SECONDS` 和 `_should_retry_tunnel_connect`）。连接拒绝错误会重试最多 3 秒以考虑跳板机延迟。

### IL 文件上传缓存
`load_il()` 通过 MD5 哈希缓存已上传文件以避免重复上传。缓存存储在 `_il_upload_cache: dict[path -> (md5, remote_path)]` 中。

### 多 Profile 实现
Profile 通过环境变量后缀实现。`SSHClient.is_running(profile)` 从 `~/.virtuoso_bridge/state_*.json` 读取状态。每个 profile 有独立的 SSH 隧道和端口。

### Spectre PATH 解析
在远程主机上，Spectre 通过以下方式定位：
1. 直接 `which spectre`（如果已在 PATH 中则有效）
2. 在 csh 子 shell 中 source `VB_CADENCE_CSHRC` 并重试

每次命令都会重新运行，因为 SSH 会话是无状态的。

### X11 对话框恢复
当模态对话框阻塞 CIW 时，SKILL 通道会超时。`dismiss_dialog()` 方法完全绕过 SKILL：
1. SSH 到远程
2. 使用 `xwininfo` 查找 virtuoso 拥有的对话框窗口
3. 通过 `XTestFakeKeyEvent` 发送回车键

## 无 Virtuoso 测试

大多数功能需要运行的 Virtuoso 实例。无 Virtuoso 的单元测试：
- Mock `VirtuosoClient.execute_skill()` 返回值
- 测试 SKILL 字符串组合函数
- 测试文件路径处理和 SSH 命令生成

## 代码风格约定

- **类型提示**：所有公共函数必须使用
- **SKILL 字符串转义**：使用 `virtuoso.ops` 中的 `escape_skill_string()`
- **超时处理**：始终传播 timeout 参数，默认 30s
- **错误处理**：返回带有 `ExecutionStatus.ERROR` 的 `VirtuosoResult`，不要为预期失败抛出异常
- **路径处理**：远程路径使用 `Path.as_posix()`（始终正斜杠）

## 常见陷阱

- **CIW 输出 vs 返回值**：`execute_skill()` 返回给 Python 但不在 CIW 中打印。在 SKILL 中使用 `printf()` 在 CIW 中显示。
- **阻塞操作**：不要在 Maestro 调用中使用 `?waitUntilDone t`（死锁）。使用异步运行 + `maeWaitUntilDone()`。
- **对话框阻塞**：如果 `execute_skill()` 超时，可能是 GUI 对话框阻塞。使用 `virtuoso-bridge dismiss-dialog` 或 `client.dismiss_dialog()`。
- **CDF 参数**：使用 `schHiReplace()` 设置值，然后使用 `CCSinvokeCdfCallbacks()` 触发更新。永远不要直接设置 `param~>value`。
- **本地 vs 远程路径**：`upload_file()`/`download_file()` 自动处理翻译。
