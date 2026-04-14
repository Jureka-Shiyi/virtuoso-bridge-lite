# AGENTS.md — AI Agent 指南 (virtuoso-bridge-lite)

通过 Python 控制 Cadence Virtuoso — 远程通过 SSH 或本地在同一台机器上。

## 两种模式

| 模式 | 适用场景 | 配置方式 |
|---|---|---|
| **远程模式** | Virtuoso 在服务器上，你在本地工作 | 在 `.env` 中设置 `VB_REMOTE_HOST`，运行 `virtuoso-bridge start` |
| **本地模式** | Virtuoso 在你自己的机器上 | 在 CIW 中加载 `core/ramic_bridge.il`，使用 `VirtuosoClient.local()` |

## 前置条件

1. **SSH**: `ssh my-server` 必须能够无密码提示地工作。
2. **Virtuoso**（用于 SKILL 执行）：远程（或本地）机器上运行的 Virtuoso 进程。
3. **Spectre**（仅用于仿真）：`spectre` 在 PATH 中，或设置 `VB_CADENCE_CSHRC` 指向添加 Cadence 工具到 PATH 的 cshrc。

> Virtuoso 和 Spectre 是**独立的**——你可以运行 Spectre 而不需要 SKILL bridge，反之亦然。

## 分步设置（远程模式）

**1. 安装**

> **使用 `uv` + 虚拟环境** — 永远不要安装到全局 Python。

```bash
uv venv .venv && source .venv/bin/activate   # Windows: source .venv/Scripts/activate
uv pip install -e .
```

**2. 生成配置**

```bash
virtuoso-bridge init        # 在当前目录创建 .env 模板
```

**3. 编辑 `.env`**

> **`.env` 放哪里:** 可以放在 virtuoso-bridge-lite 目录或项目根目录（两者都会自动搜索）。当 virtuoso-bridge-lite 是子目录时，推荐放在项目根目录。

```dotenv
VB_REMOTE_HOST=my-server              # ~/.ssh/config 中的 SSH 主机别名
VB_REMOTE_USER=username               # 远程 SSH 用户名
VB_REMOTE_PORT=65081                  # 远程 bridge 守护进程的端口
VB_LOCAL_PORT=65082                   # 通过 SSH 隧道转发的本地端口

# 可选 — 仅在远程 shell 中 spectre 不在 PATH 时需要。
# VB_CADENCE_CSHRC=/path/to/.cshrc   # 在远程设置 Cadence 工具的 cshrc
```

**4. 启动 bridge**

```bash
virtuoso-bridge start
```

**5. 在 Virtuoso CIW 中加载 SKILL**

```
load("/path/to/virtuoso-bridge-lite/core/ramic_bridge.il")
```

**6. 验证**

```bash
virtuoso-bridge status
```

**7. 从 Python 连接**

```python
from virtuoso_bridge import VirtuosoClient
client = VirtuosoClient.from_env()
client.execute_skill("1+2")  # VirtuosoResult(status=SUCCESS, output='3')
```

> **CIW 输出 vs 返回值**: `execute_skill()` 将结果返回给 Python 但**不会**在 CIW 窗口中打印。如需也在 CIW 中显示，请显式使用 `printf`:
> `client.execute_skill(r'let((v) v=1+2 printf("1+2 = %d\n" v) v)')`。
> 参见 `examples/01_virtuoso/basic/00_ciw_output_vs_return.py`。

### 跳板机设置

如果你需要通过堡垒机/跳板机访问 Virtuoso，在 `.env` 中设置两个主机：

```dotenv
VB_REMOTE_HOST=compute-host   # 运行 Virtuoso 的机器（不是跳板机）
VB_JUMP_HOST=jump-host        # 你 SSH 到的堡垒机
```

常见错误：把 `VB_REMOTE_HOST` 设置为跳板机。`VB_REMOTE_HOST` 必须是实际运行 Virtuoso 的机器。

### 多 Profile 设置

用 `-p` 同时连接多个 Virtuoso 实例。Profile 名称**区分大小写**，作为后缀添加到环境变量名。

```dotenv
# 默认（无 profile）
VB_REMOTE_HOST=server-a
VB_REMOTE_USER=user1

# Profile "worker1" — 配合 `-p worker1` 使用
VB_REMOTE_HOST_worker1=server-b
VB_USER_worker1=user2
VB_CADENCE_CSHRC_worker1=/path/to/.cshrc.worker1
```

```bash
virtuoso-bridge start -p worker1
virtuoso-bridge status -p worker1
```

```python
from virtuoso_bridge.spectre import SpectreSimulator
sim = SpectreSimulator.from_env(profile="worker1")
```

> Profile 后缀区分大小写。`-p worker1` 读取 `VB_REMOTE_HOST_worker1`，而不是 `VB_REMOTE_HOST_WORKER1`。

## 首次设置检查

当用户首次打开此项目时，在做任何其他操作之前运行以下检查：

### 远程检查

**三主机模型**（EDA 环境中常见）：
```
你的机器  ──SSH──►  跳板机（堡垒）  ──SSH──►  计算主机（Virtuoso）
              VB_JUMP_HOST                   VB_REMOTE_HOST
```
`VB_REMOTE_HOST` 必须是运行 Virtuoso 的机器，**不是**跳板机。这是最常见的配置错误。

1. **检查 `.env`** — 是否存在且设置了 `VB_REMOTE_HOST`？
   - 如果没有：`pip install -e .` 然后 `virtuoso-bridge init`，让用户填写 SSH 主机。
   - 验证：`VB_REMOTE_HOST` = 计算主机（Virtuoso 运行的地方），`VB_JUMP_HOST` = 堡垒机（如有）。

2. **检查 SSH** — `ssh <VB_REMOTE_HOST> echo ok`（或通过配置的跳板机）
   - 如果失败：告诉用户先修复 SSH。Bridge 假设 `ssh <host>` 已经可用。

3. **检查 Virtuoso** — `ssh <VB_REMOTE_HOST> "pgrep -f virtuoso"`
   - 如果没有进程：告诉用户先启动 Virtuoso。

4. **启动 bridge** — `virtuoso-bridge start`
   - 如果显示 "degraded"：告诉用户在 Virtuoso CIW 中粘贴 `load("...")` 命令。

5. **验证** — `virtuoso-bridge status`

6. **快速测试** — `VirtuosoClient.from_env().execute_skill("1+2")`

### 本地模式

无隧道，无 `.env`，无 SSH。只需在 Virtuoso CIW 中加载 `core/ramic_bridge.il` 然后直接连接。

```python
from virtuoso_bridge import VirtuosoClient
bridge = VirtuosoClient.local(port=65432)
bridge.execute_skill("1+2")
```

## 架构

两个解耦的层：

- **VirtuosoClient** — 纯 TCP SKILL 客户端。无 SSH。可与任何 `localhost:port` 端点配合工作。
- **SSHClient** — 管理 SSH 隧道 + 远程守护进程部署。可选。

```python
# 远程：SSHClient 创建 TCP 路径
from virtuoso_bridge import SSHClient, VirtuosoClient
tunnel = SSHClient.from_env()
tunnel.warm()
bridge = VirtuosoClient.from_tunnel(tunnel)

# 本地：不需要隧道
bridge = VirtuosoClient.local(port=65432)

# 两种方式，API 相同：
bridge.execute_skill("1+2")
```

## 两个独立服务

Bridge 在远程主机上管理两个**独立**的能力：

| 服务 | 功能 | 要求 |
|---|---|---|
| **Virtuoso 守护进程** | 在 Virtuoso CIW 中执行 SKILL 表达式 | 运行的 Virtuoso 进程 + 在 CIW 中 `load("...virtuoso_setup.il")` |
| **Spectre** | 通过 SSH 运行电路仿真 | `spectre` 在 PATH 中（或设置 `VB_CADENCE_CSHRC`） |

它们完全独立——你可以在不加载 SKILL bridge 的情况下运行 Spectre，也可以在不使用 Spectre 的情况下使用 SKILL bridge。

`virtuoso-bridge status` 同时报告两者。示例输出：
```
[tunnel]  running          ← SSH 隧道已建立
[daemon]  OK               ← Virtuoso CIW 已连接（或未加载时显示 NO RESPONSE）
[spectre] OK               ← 远程找到 spectre（或 NOT FOUND）
```

### Spectre 如何定位

每个 SSH 命令都在**全新的 shell** 中运行，没有先前状态。为了找到 `spectre`，bridge：

1. 直接尝试 `which spectre` — 如果用户的登录 shell 已经有 Cadence 在 PATH 中则有效。
2. 如果未找到且设置了 `VB_CADENCE_CSHRC`，在 csh 子 shell 中 source 那个 cshrc 来设置 `PATH`、`LM_LICENSE_FILE`、`LD_LIBRARY_PATH` 等，然后重试。

这个 cshrc **每次**都会 source（状态检查、license 检查、每次仿真运行），因为每个 SSH 命令都是新进程，没有之前会话的记忆。

如果远程用户的默认 shell 中 `spectre` 已经在 PATH 中（例如通过 `~/.bashrc` 或 `~/.cshrc`），则不需要 `VB_CADENCE_CSHRC`。

## 关键约定

- 所有 SKILL 执行都通过 `VirtuosoClient`。永远不要 SSH 后手动运行 SKILL。
- Layout/schematic 编辑：`client.layout.edit()` / `client.schematic.edit()` 上下文管理器。
- Spectre 仿真：`SpectreSimulator.from_env()`。参见上面的 "Spectre 如何定位"。
- `core/` 用于理解机制（3 个文件，180 行）。实际工作使用已安装的包。

## 常见陷阱

- **`csh()` 返回 `t`/`nil`**，不是命令输出。使用 `client.download_file()`（SSH/SCP）进行远程文件操作。
- **`procedurep()` 对编译/内置函数返回 `nil`**。不要用它来检查 `mae*` 函数是否存在。
- **远程文件留在远程。** 像 `maeCreateNetlistForCorner` 这样的函数写入远程文件系统。使用 `client.download_file()` 检索它们。

## 如何配置 PDK 路径

从 Virtuoso 导出网表（**Simulation > Netlist > Create**）。`.scs` 文件包含所有内容：

```spectre
include "/path/to/pdk/models/spectre/toplevel.scs" section=TOP_TT
M0 (VOUT VIN VSS VSS) nch_ulvt_mac l=30n w=1u nf=1
```

## CLI 参考

```bash
virtuoso-bridge init      # 创建 .env 模板
virtuoso-bridge start     # 启动 SSH 隧道 + 部署守护进程
virtuoso-bridge restart   # 强制重启
virtuoso-bridge status    # 检查隧道 + Virtuoso 守护进程 + Spectre
```

## 构建与测试

> **推荐：使用 `uv` 管理虚拟环境。** `uv` 拒绝全局安装包（除非显式传递 `--system`），防止意外污染系统 Python。

```bash
uv venv .venv && source .venv/bin/activate   # Windows: source .venv/Scripts/activate
uv pip install -e ".[dev]"
pytest
```

## Windows：修复符号链接

Git on Windows 将符号链接克隆为纯文本文件（`core.symlinks = false`），
这会破坏任何遵循 `.claude/skills/`（或类似）链接的 agent 的 SKILL 加载。克隆后运行一次：

```bash
bash scripts/fix-symlinks.sh
```

该脚本用 NTFS junction 替换损坏的符号链接——不需要管理员权限，不需要开发者模式。

## Skills

| Skill | 文件 | 覆盖范围 |
|---|---|---|
| `virtuoso` | `skills/virtuoso/SKILL.md` | SKILL 执行、layout/schematic 编辑 |
| `spectre` | `skills/spectre/SKILL.md` | 仿真、结果解析 |

```
skills/virtuoso/
  SKILL.md
  references/
    layout.md       # layout API 参考
    schematic.md    # schematic API 参考

skills/spectre/
  SKILL.md          # 仿真工作流 + 结果解析
```
