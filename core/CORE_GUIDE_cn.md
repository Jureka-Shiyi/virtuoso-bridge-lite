# core/ 目录文件详解

本目录包含 **virtuoso-bridge-lite** 的核心机制实现，仅用 **4 个文件、约 180 行代码** 展示了整个桥接系统的底层原理。这是理解项目架构的最佳起点。

---

## 文件概览

| 文件名 | 语言 | 行数 | 作用 | 运行位置 |
|--------|------|------|------|----------|
| `ramic_bridge.il` | SKILL | 38 | Virtuoso 端 IPC 服务端 | 远程 Virtuoso CIW |
| `ramic_daemon.py` | Python | 126 | TCP 到 Virtuoso 的守护进程 | 远程服务器 |
| `bridge_client.py` | Python | 46 | Python 客户端 | 本地机器 |
| `README.md` | Markdown | - | 架构说明文档 | - |

---

## 1. ramic_bridge.il - SKILL 端 IPC 服务端

### 功能概述

这是运行在 **Cadence Virtuoso** 内部的 SKILL 脚本，负责在 Virtuoso CIW（Command Interpreter Window）中启动 IPC（进程间通信）服务，接收来自 Python 客户端的 SKILL 代码并执行。

### 代码详解

```skill
; RAMIC Bridge — minimal SKILL-side IPC
; Load this in Virtuoso CIW: load("/path/to/ramic_bridge.il")

RBPort = 65432
```

**全局变量 `RBPort`**：定义守护进程监听的 TCP 端口（默认 65432）。

---

#### 核心过程 1: `RBIpcDataHandler`

```skill
procedure(RBIpcDataHandler(ipcId data)
  let((result)
    if(errset(result = evalstring(data)) then
      ipcWriteProcess(ipcId sprintf(nil "%c%L%c" 2 result 30))
    else
      ipcWriteProcess(ipcId sprintf(nil "%c%L%c" 21 errset.errset 30))
    )
  )
)
```

**功能**：处理从守护进程收到的 SKILL 代码。

**工作流程**：
1. 接收 `data`（字符串形式的 SKILL 表达式）
2. 使用 `evalstring()` 执行代码
3. **成功**：返回 `\x02` (STX) + 结果 + `\x1e` (RS)
4. **失败**：返回 `\x15` (NAK) + 错误信息 + `\x1e` (RS)

**关键函数**：
- `errset()` - SKILL 的错误捕获机制，防止脚本崩溃
- `ipcWriteProcess()` - 向守护进程写入响应
- `sprintf()` - 格式化输出，使用 `\x02` 和 `\x15` 作为状态前缀

---

#### 核心过程 2: `RBIpcFinishHandler`

```skill
procedure(RBIpcFinishHandler(ipcId data)
  printf("[RAMIC] daemon exited\n")
)
```

**功能**：当守护进程退出时的回调，在 CIW 中打印退出消息。

---

#### 核心过程 3: `RBStart`

```skill
procedure(RBStart()
  if(boundp('RBIpc) && ipcIsAliveProcess(RBIpc) then
    printf("[RAMIC] already running\n")
  else
    RBIpc = ipcBeginProcess(
      sprintf(nil "/usr/bin/env -u LD_LIBRARY_PATH -u LD_PRELOAD python %s %s %d"
        strcat(getShellEnvVar("RB_DAEMON_PATH") || "." "/ramic_daemon.py")
        "127.0.0.1" RBPort)
      "" 'RBIpcDataHandler nil 'RBIpcFinishHandler "")
    printf("[RAMIC] started on port %d\n" RBPort)
  )
)

RBStart()
```

**功能**：启动 IPC 进程和 Python 守护进程。

**关键步骤**：
1. 检查是否已有运行的实例（避免重复启动）
2. 使用 `ipcBeginProcess()` 启动 Python 守护进程
3. 通过 `env -u` 清除 Virtuoso 的环境变量，避免 Python 链接冲突
4. 支持通过 `RB_DAEMON_PATH` 环境变量指定守护进程路径

**命令分解**：
```bash
/usr/bin/env -u LD_LIBRARY_PATH -u LD_PRELOAD python <daemon_path> 127.0.0.1 65432
```

---

## 2. ramic_daemon.py - TCP 中继守护进程

### 功能概述

这是运行在 **远程服务器** 上的守护进程，作为 **TCP 套接字** 和 **Virtuoso IPC 管道** 之间的桥梁：
- 监听 TCP 连接（来自本地 Python 客户端）
- 将收到的 SKILL 代码转发给 Virtuoso
- 将 Virtuoso 的执行结果返回给客户端

### 代码详解

#### 模块导入和常量定义

```python
import sys
import socket
import os
import fcntl
import json
import errno
import time
import re

HOST = sys.argv[1]  # 绑定的主机地址
PORT = int(sys.argv[2])  # 监听的端口
```

**协议常量**：
```python
STX = b'\x02'  # Start of Text - 成功标记
NAK = b'\x15'  # Negative Acknowledge - 错误标记
RS  = b'\x1e'  # Record Separator - 记录结束标记
```

#### 非阻塞 stdin 设置

```python
fcntl.fcntl(sys.stdin.fileno(), fcntl.F_SETFL,
            fcntl.fcntl(sys.stdin.fileno(), fcntl.F_GETFL) | os.O_NONBLOCK)
```

**作用**：将标准输入设为非阻塞模式，以便从 Virtuoso 接收数据时不会卡住。

---

#### 核心函数: `read_result()`

```python
def read_result():
    """Read one delimited result from Virtuoso via stdin."""
    buf = bytearray()
    started = False
    while True:
        try:
            ch = sys.stdin.read(1)
            if not ch:
                time.sleep(0.001)
                continue
            if not started:
                if ch in (STX, NAK, '\x02', '\x15'):
                    started = True
                    buf.extend(ch.encode('latin1') if isinstance(ch, str) else ch)
                continue
            if ch in (RS, '\x1e'):
                break
            buf.extend(ch.encode('latin1') if isinstance(ch, str) else ch)
        except IOError as e:
            if e.errno in (errno.EAGAIN, errno.EWOULDBLOCK):
                time.sleep(0.001)
                continue
            raise
    return bytes(buf)
```

**功能**：从 Virtuoso 读取一个完整的执行结果。

**协议解析**：
1. 等待起始标记（`\x02` 或 `\x15`）
2. 持续读取数据直到结束标记（`\x1e`）
3. 处理非阻塞 I/O 的 `EAGAIN` 错误

---

#### 安全函数: `_check_skill()`

```python
_BLOCKED_FNS = re.compile(
    r'(?<!"\w])(shell|system|ipcBeginProcess|getShellEnvVar|sstGetUserName)\s*\(',
)

def _check_skill(skill: str) -> None:
    """Reject SKILL code that calls dangerous shell-access functions."""
    stripped = re.sub(r'"[^"]*"', '""', skill)  # 移除字符串内容
    m = _BLOCKED_FNS.search(stripped)
    if m:
        raise ValueError(f"Blocked SKILL function: {m.group(1)!r}")
```

**功能**：安全检查，阻止执行危险的 SKILL 函数。

**被阻止的函数**：
- `shell()` / `system()` - 执行系统命令
- `ipcBeginProcess()` - 创建新进程
- `getShellEnvVar()` - 读取环境变量
- `sstGetUserName()` - 获取用户信息

**安全策略**：先移除所有字符串内容（避免误报），再正则匹配危险函数调用。

---

#### 核心处理函数: `handle()`

```python
def handle(conn):
    """Handle one client request."""
    chunks = []
    while True:
        chunk = conn.recv(65536)
        if not chunk:
            break
        chunks.append(chunk)
    req = json.loads(b"".join(chunks))

    # 多行 SKILL 压缩为单行（处理注释）
    skill = re.sub(r'"[^"]*"|;[^\n]*', 
                   lambda m: m.group() if m.group().startswith('"') else ' ', 
                   req["skill"])
    skill = ' '.join(skill.split())  # 压缩空白字符

    _check_skill(skill)

    # 发送 SKILL 到 Virtuoso
    sys.stdout.write(skill)
    sys.stdout.flush()

    # 读取结果并返回
    result = read_result()
    conn.sendall(result)
```

**功能**：处理单个客户端请求。

**处理流程**：
1. 接收 JSON 格式的请求（包含 `skill` 字段）
2. **预处理**：将多行 SKILL 压缩为单行，移除 `;` 注释
3. **安全检查**：验证没有危险函数调用
4. **转发**：通过 stdout 发送给 Virtuoso
5. **响应**：从 stdin 读取结果，通过 TCP 返回给客户端

---

#### 主循环: `main()`

```python
def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen(1)
    while True:
        conn, _ = s.accept()
        try:
            handle(conn)
        except Exception as e:
            try:
                conn.sendall(('\x15' + str(e)).encode('utf-8'))
            except:
                pass
        finally:
            conn.shutdown(socket.SHUT_RDWR)
            conn.close()
```

**功能**：TCP 服务器主循环。

**特点**：
- 单线程顺序处理（每次一个连接）
- 支持地址复用（`SO_REUSEADDR`）
- 异常时返回错误信息给客户端
- 确保连接正确关闭

---

## 3. bridge_client.py - Python 客户端

### 功能概述

这是运行在 **本地机器** 的极简客户端，演示如何通过 TCP 连接发送 SKILL 代码并获取结果。

### 代码详解

#### 核心函数: `execute_skill()`

```python
def execute_skill(skill_code, host="127.0.0.1", port=65432, timeout=30):
    """Send a SKILL expression, return the result string."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    s.sendall(json.dumps({"skill": skill_code, "timeout": timeout}).encode())
    s.shutdown(socket.SHUT_WR)
    data = b""
    while True:
        chunk = s.recv(65536)
        if not chunk:
            break
        data += chunk
    s.close()
    # 第一个字节: \x02 = 成功, \x15 = 错误
    if data and data[0:1] == b'\x02':
        return {"ok": True, "result": data[1:].decode("utf-8", errors="replace")}
    else:
        return {"ok": False, "error": data[1:].decode("utf-8", errors="replace")}
```

**功能**：建立 TCP 连接，发送 SKILL 代码，接收并解析结果。

**请求格式**（JSON）：
```json
{
  "skill": "1+2",
  "timeout": 30
}
```

**响应解析**：
- 第一个字节是状态码：`\x02` 成功，`\x15` 失败
- 剩余字节是结果或错误信息

---

#### 命令行接口

```python
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python bridge_client.py '<SKILL expression>'")
        sys.exit(1)
    result = execute_skill(sys.argv[1])
    if result["ok"]:
        print(result["result"])
    else:
        print(f"ERROR: {result['error']}", file=sys.stderr)
        sys.exit(1)
```

**使用示例**：
```bash
# 执行简单计算
python bridge_client.py '1+2'
# 输出: 3

# 获取 Virtuoso 当前窗口
python bridge_client.py 'hiGetCurrentWindow()'

# 获取编辑中的单元
python bridge_client.py 'geGetEditCellView()~>cellName'
```

---

## 4. README.md - 架构说明文档

该文件提供了 `core/` 目录的概述和使用指南，包括：

- **快速开始**：如何手动设置和运行核心组件
- **架构图解**：展示数据流向
- **与完整包的对比**：说明 `core/` 仅用于理解机制

**核心要点**：
> `core/` 是用于理解机制的。对于生产使用，请安装完整包（`pip install -e .`），它增加了 SSHClient（自动 SSH 隧道、重连、文件传输）和 VirtuosoClient（layout/schematic API、Spectre 集成）。

---

## 工作流程图解

```
本地机器                              远程 Virtuoso 服务器
─────────                            ─────────────────────

bridge_client.py                      Virtuoso 进程
(= VirtuosoClient)                       (= ramic_bridge.il)
    │                                     │
    │ TCP: {"skill":"1+2"}                │
    ├──── SSH 隧道 ────────────► ramic_daemon.py
    │     (= SSHClient)               │
    │                                     │ stdout: "1+2"
    │                                     ├──► evalstring("1+2")
    │                                     │        │
    │                                     │        ▼
    │                                     │ stdin: "\x02 3 \x1e"
    │                                     ◄──┘
    │ TCP: "\x02 3"                       │
    ◄──── SSH 隧道 ─────────────┘
    │
    ▼
   "3"
```

**数据流**：
1. **本地** Python 客户端通过 TCP 发送 JSON 请求
2. **远程** 守护进程接收并转发给 Virtuoso
3. **Virtuoso** 执行 SKILL 代码
4. **Virtuoso** 通过 IPC 返回结果给守护进程
5. **守护进程** 通过 TCP 返回给本地客户端

---

## 文件关系图

```
┌─────────────────────────────────────────────────────────┐
│                      本地机器                            │
│  ┌─────────────────┐                                    │
│  │ bridge_client.py│  ─── TCP (SSH 隧道) ───┐           │
│  │   (Python)      │                       │           │
│  └─────────────────┘                       │           │
└────────────────────────────────────────────┼───────────┘
                                             │
                                        SSH 隧道
                                             │
┌────────────────────────────────────────────┼───────────┐
│                    远程服务器               │           │
│  ┌─────────────────────────────────────────┘           │
│  │                                                     │
│  │  ┌───────────────┐         ┌─────────────────┐     │
│  │  │ramic_daemon.py│◄───────►│  Virtuoso 进程  │     │
│  │  │   (Python)    │  stdin  │                 │     │
│  │  │               │ stdout  │ ┌─────────────┐ │     │
│  │  │  TCP ◄───────►│◄───────►│ │ramic_bridge.│ │     │
│  │  │  服务端       │  IPC    │ │    il       │ │     │
│  │  └───────────────┘         │ │  (SKILL)    │ │     │
│  │                            │ └─────────────┘ │     │
│  │                            └─────────────────┘     │
│  │                                                     │
│  └─────────────────────────────────────────────────────┘
│
└─────────────────────────────────────────────────────────┘
```

---

## 使用步骤

### 手动运行（不使用 SSH 隧道）

**步骤 1**: 复制守护进程到远程服务器
```bash
scp core/ramic_daemon.py remote:/tmp/
```

**步骤 2**: 在 Virtuoso CIW 中加载 SKILL 脚本
```skill
load("/tmp/ramic_bridge.il")
```

**步骤 3**: 启动守护进程（自动完成）

**步骤 4**: 本地运行客户端
```bash
python core/bridge_client.py '1+2'
```

### 使用 SSH 隧道

```bash
# 创建 SSH 隧道
ssh -N -L 65432:localhost:65432 remote &

# 运行客户端
python core/bridge_client.py 'hiGetCurrentWindow()'
```

---

## 与完整包的区别

| 特性 | core/ (精简版) | 完整包 (src/) |
|------|----------------|---------------|
| SSH 隧道 | 手动设置 | 自动管理 (`SSHClient`) |
| 文件传输 | 手动 scp | `upload_file()` / `download_file()` |
| 布局/原理图 API | 原始 SKILL | 高级 Python API (`layout.edit()`, `schematic.edit()`) |
| Spectre 仿真 | 不支持 | `SpectreSimulator` 类 |
| 重连机制 | 无 | 自动重连 |
| 多配置文件 | 不支持 | 支持多服务器配置 |

---

## 扩展开发

如果你想基于 `core/` 进行扩展：

1. **添加新命令**：修改 `ramic_daemon.py` 的 `handle()` 函数
2. **增强安全**：扩展 `_BLOCKED_FNS` 正则表达式
3. **支持异步**：将 `main()` 改为多线程或使用 `asyncio`
4. **添加身份验证**：在 TCP 连接中添加密钥验证

---

*本文档详细解释了 core/ 目录下每个文件的功能和实现细节。如需了解生产级功能，请参考 src/virtuoso_bridge/ 目录。*
