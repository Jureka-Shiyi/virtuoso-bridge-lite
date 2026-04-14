---
name: virtuoso
description: "通过 Python API 桥接到远程 Cadence Virtuoso。触发条件：用户提及 Virtuoso、Maestro、ADE、CIW、SKILL、layout、schematic、cellview、OCEAN 或任何 Cadence EDA 操作。"
---

# Virtuoso Skill

> **关键：不要凭记忆发明 SKILL 代码或 API 调用。**
> 在编写任何 SKILL 表达式或调用任何 Python API 函数之前：
> 1. **搜索 `references/`** 查找函数名或关键字
> 2. **查看 `examples/`** 寻找相同操作的示例
> 3. **阅读实际函数签名**（Python 用 `help()`，SKILL 用 `references/*.md`）
>
> 如果函数在 references 或 examples 中没有记录，它可能不存在或名称不同。永远不要猜测参数名——先验证。

## 思维模型

你通过 `virtuoso-bridge` 控制远程 Cadence Virtuoso。Python 在本地运行；SKILL 在远程 Virtuoso CIW 中执行。SSH 隧道自动建立。

```
 本地 (Python)                    远程 (Virtuoso)
┌──────────────────┐   SSH tunnel  ┌──────────────────┐
│ VirtuosoClient   │ ────────────► │ CIW (SKILL)      │
│                  │               │                  │
│ • schematic.*    │               │ • dbCreateInst   │
│ • layout.*      │               │ • schCreateWire  │
│ • execute_skill │               │ • mae*           │
│ • load_il       │               │ • dbOpenCellView │
└──────────────────┘               └──────────────────┘
```

### 三个抽象层级

| 层级 | 使用场景 | 示例 |
|-------|---------|------|
| **Python API** | 原理图/布局编辑——结构化、安全 | `client.schematic.edit(lib, cell)` |
| **内联 SKILL** | Maestro、CDF 参数、API 未覆盖的任何内容 | `client.execute_skill('maeRunSimulation()')` |
| **SKILL 文件** | 批量操作、复杂循环 | `client.load_il("my_script.il")` |

始终使用最高层级且能工作的。只在需要时才降级。

**永远不要猜测函数名。** 如果函数不在下面的示例中，先阅读相关的 `references/` 文件再编写调用。编造错误的名称会浪费在 CIW 中调试的时间。

### 四个领域

| 领域 | 功能 | Python 包 | API 文档 |
|------|------|----------|----------|
| **Schematic** | 创建/编辑原理图、连线实例、添加引脚 | `client.schematic.*` | `references/schematic-python-api.md`, `references/schematic-skill-api.md` |
| **Layout** | 创建/编辑布局、添加形状/过孔/实例 | `client.layout.*` | `references/layout-python-api.md`, `references/layout-skill-api.md` |
| **Maestro** | 读/写 ADE Assembler 配置、运行仿真 | `virtuoso_bridge.virtuoso.maestro` | `references/maestro-python-api.md`, `references/maestro-skill-api.md` |
| **Netlist (si)** | 批量网表生成（无需 Maestro） | `simInitEnvWithArgs` + `si` CLI | 参见下面的"批量网表 (si)"部分 |
| **通用** | 文件传输、截图、原始 SKILL、.il 加载 | `client.*` | 参见下文 |

## 开始之前

### 环境设置

> **`virtuoso-bridge` 是一个 Python CLI。** 使用 `uv` + 虚拟环境——永远不要安装到全局 Python。

```bash
uv venv .venv && source .venv/bin/activate   # Windows: source .venv/Scripts/activate
uv pip install -e virtuoso-bridge-lite
```

所有 `virtuoso-bridge` CLI 命令和 Python 脚本必须在激活的 venv 中运行。

### 连接顺序（按顺序执行）

1. **检查 `.env`** — 如果项目还没有 `.env`，运行 **`virtuoso-bridge init`** 创建。如果 `.env` 已存在，跳过 `init`。
2. **`virtuoso-bridge start`** — 启动本地桥接服务和 SSH 隧道。
3. **如果状态是 `degraded`** — 用户需要在 Virtuoso CIW 中加载 setup 脚本（`start` 输出会告诉他们具体要运行什么）。
4. **`virtuoso-bridge status`** — 在继续之前验证一切都是 `healthy`。

### 然后

- **先查看示例**：`examples/01_virtuoso/` — 不要从零开始造轮子。
- **打开窗口**：`client.open_window(lib, cell, view="layout")` 以便用户看到你在做什么。

## 客户端基础

```python
from virtuoso_bridge import VirtuosoClient
client = VirtuosoClient.from_env()

client.execute_skill('...')                     # 运行 SKILL 表达式
client.load_il("my_script.il")                  # 上传 + 加载 .il 文件
client.upload_file(local_path, remote_path)      # 本地 → 远程
client.download_file(remote_path, local_path)    # 远程 → 本地
client.open_window(lib, cell, view="layout")     # 打开 GUI 窗口
client.run_shell_command("ls /tmp/")             # 在远程运行 shell 命令
```

### CIW 输出 vs 返回值

`execute_skill()` 将结果返回给 Python，但**不会**在 CIW 窗口中打印任何内容。这是设计使然——桥接是一个程序化 API，不是交互式 REPL。

```python
# 仅返回值 — CIW 保持静默
r = client.execute_skill("1+2")        # Python 得到 3，CIW 无显示

# 要在 CIW 中也显示，使用 printf
r = client.execute_skill(r'let((v) v=1+2 printf("1+2 = %d\n" v) v)')
#   Python 得到 3，CIW 显示 "1+2 = 3"
```

完整示例：`examples/01_virtuoso/basic/00_ciw_output_vs_return.py`

## 向 CIW 打印多行文本

在单个 `execute_skill()` 中发送多个 `printf()` 会丢失换行符——CIW 会将所有内容连接在一行上。要打印多行文本，将其写成 Python 多行字符串，每行发送一个 `execute_skill()`：

```python
text = """\
========================================
  Title goes here
========================================
  First paragraph line one.
  First paragraph line two.

  Second paragraph.
========================================"""

for line in text.splitlines():
    client.execute_skill('printf("' + line + '\\n")')
```

限制：
- **仅 ASCII** — 表情符号和 CJK 字符会导致远程 SKILL 解释器上的 JSON 编码错误
- **文本中不能有未转义的 SKILL 特殊字符** — 如果行可能包含 `"` 或 `%`，请转义它们（`\\"`、`%%`）或改用 `load_il()`（参见 `03_load_il.py`）

> **重要：始终编写 `.py` 文件，永远不要使用 `python -c`。**
> `python -c "..."` 有三层引用（shell + Python + SKILL）。`\\n` 很容易变成 `\\\\n`，导致 `printf` 静默不产生输出。
> 始终将代码写入 `.py` 文件并运行 `python script.py`——只有两层引用（Python + SKILL），与示例匹配。

完整示例：`examples/01_virtuoso/basic/02_ciw_print.py`

## 参考资料

按需加载——每个都包含详细的 API 文档和边界情况指导：

| 文件 | 内容 |
|------|------|
| `references/schematic-skill-api.md` | 原理图 SKILL API、端子感知辅助函数、CDF 参数 |
| `references/schematic-python-api.md` | SchematicEditor、SchematicOps、低级构建器 |
| `references/layout-skill-api.md` | 布局 SKILL API、读/查询、镶嵌、层控制 |
| `references/layout-python-api.md` | LayoutEditor、LayoutOps、形状/过孔/实例创建 |
| `references/maestro-skill-api.md` | mae* SKILL 函数、OCEAN、角落、已知阻塞点 |
| `references/maestro-python-api.md` | Session、read_config (verbose 0/1/2)、写入函数 |
| `references/netlist.md` | CDL/Spectre 网表格式、spiceIn 导入 |
| `references/troubleshooting.md` | 已知陷阱、GUI 阻塞、CDF 怪癖、连接问题 |
| `references/testbench-migration.md` | 将测试台 + Maestro 迁移到另一个库（陷阱、CDF 参数名） |
| `references/schematic-recreation.md` | 从现有设计重新创建原理图（网格布局、差分对约定） |
| `references/batch-netlist-si.md` | 使用 si 批量翻译器生成网表（无需 Maestro） |

## 示例

**编写新代码前始终查看这些。**

### `examples/01_virtuoso/basic/`
- `00_ciw_output_vs_return.py` — CIW 输出 vs Python 返回值（CIW 何时打印、何时不打印）
- `01_execute_skill.py` — 运行任意 SKILL 表达式
- `02_ciw_print.py` — 向 CIW 打印消息（每行一个 `execute_skill`）
- `03_load_il.py` — 上传和加载 .il 文件
- `04_list_library_cells.py` — 列出库和单元
- `05_multiline_skill.py` — 带注释、循环、过程的 multi-line SKILL
- `06_screenshot.py` — 捕获布局/原理图截图

### `examples/01_virtuoso/schematic/`
- `01a_create_rc_stepwise.py` — 通过操作创建 RC 原理图
- `01b_create_rc_load_skill.py` — 通过 .il 脚本创建 RC 原理图
- `02_read_connectivity.py` — 读取实例连接和网络
- `03_read_instance_params.py` — 读取 CDF 实例参数
- `05_rename_instance.py` — 重命名原理图实例
- `06_delete_instance.py` — 删除实例
- `07_delete_cell.py` — 从库中删除单元
- `08_import_cdl_cap_array.py` — 通过 spiceIn 导入 CDL 网表（SSH）

### `examples/01_virtuoso/layout/`
- `01_create_layout.py` — 创建带矩形、路径、实例的布局
- `02_add_polygon.py` — 添加多边形
- `03_add_via.py` — 添加过孔
- `04_multilayer_routing.py` — 多层布线
- `05_bus_routing.py` — 总线布线
- `06_read_layout.py` — 读取布局形状
- `07–10` — 删除/清除操作

### `examples/01_virtuoso/maestro/`
- `01_read_open_maestro.py` — 从当前打开的 maestro 读取配置
- `02_gui_open_read_close_maestro.py` — GUI 打开 → 读取配置 → 关闭
- `03_bg_open_read_close_maestro.py` — 后台打开 → 读取配置 → 关闭
- `04_read_env.py` — 读取环境设置（模型文件、仿真选项、运行模式）
- `05_read_results.py` — 读取仿真结果（输出值、规格、良率）
- `06a_rc_create.py` — 创建 RC 原理图 + Maestro 设置
- `06b_rc_simulate.py` — 运行仿真
- `06c_rc_read_results.py` — 读取结果、导出波形、打开 GUI

## 常见工作流程

### 查找包含某个单元的库

带单个参数调用 `ddGetObj(cellName)` 返回 nil——必须遍历 `ddGetLibList()`：

```python
r = client.execute_skill(f'''
let((result)
  result = nil
  foreach(lib ddGetLibList()
    when(ddGetObj(lib~>name "{CELL}")
      result = cons(lib~>name result)))
  result)
''')
# r.output 例如: '("2025_FIA")'
```

无需单独的脚本——在任何需要定位单元的工作流程中内联使用。

### 创建原理图

```python
from virtuoso_bridge.virtuoso.schematic import (
    schematic_create_inst_by_master_name as inst,
    schematic_create_pin as pin,
)

with client.schematic.edit(LIB, CELL) as sch:
    # 1. 放置实例 — sch.add() 排队 SKILL 命令
    sch.add(inst("tsmcN28", "pch_mac", "symbol", "MP0", 0, 1.5, "R0"))
    sch.add(inst("tsmcN28", "nch_mac", "symbol", "MN0", 0, 0, "R0"))

    # 2. 用 stubs 标记 MOS 端子 — 不是手动 add_wire
    sch.add_net_label_to_transistor("MP0",
        drain_net="OUT", gate_net="IN", source_net="VDD", body_net="VDD")
    sch.add_net_label_to_transistor("MN0",
        drain_net="OUT", gate_net="IN", source_net="VSS", body_net="VSS")

    # 3. 在电路边缘添加引脚，不要在端子上
    sch.add(pin("IN",  -1.0, 0.75, "R0", direction="input"))
    sch.add(pin("OUT", -1.0, 0.25, "R0", direction="output"))
    # schCheck + dbSave 在上下文退出时自动发生
```

**关键规则：**
- **对 MOS D/G/S/B 使用 `add_net_label_to_transistor`**——它自动检测 stub 方向。永远不要手动在端子之间 `add_wire`。
- **引脚放在电路边缘**，不要在实例端子上。它们通过匹配的网络名称连接。
- **删除再重建**——如果 cell 已存在，`add_instance` 会累积在旧实例之上：
  ```python
  client.execute_skill(f'ddDeleteObj(ddGetObj("{LIB}" "{CELL}"))')
  ```
- **CDF 参数**——两步过程：

  **步骤 1：用 `schHiReplace` 设置值**（Edit > Replace）。不要使用 `param~>value =` 或 `dbSetq`——它们不会更新显示或派生参数。
  ```python
  client.execute_skill(
      'schHiReplace(?replaceAll t ?propName "cellName" ?condOp "==" '
      '?propValue "pch_mac" ?newPropName "w" ?newPropValue "500n")')
  ```

  **步骤 2：用 `CCSinvokeCdfCallbacks` 触发 CDF 回调**以更新派生参数（finger_width、显示注释等）。使用 `?order` 只运行更改的参数——运行所有回调可能在 PDK 特定变量（如 `mdlDir`）上失败。
  ```python
  # 必须先加载 CCSinvokeCdfCallbacks.il（一次性）
  client.upload_file("reference/CCSinvokeCdfCallbacks.il", "/tmp/CCSinvokeCdfCallbacks.il")
  client.execute_skill('load("/tmp/CCSinvokeCdfCallbacks.il")')

  # 只触发你需要的回调
  client.execute_skill('CCSinvokeCdfCallbacks(geGetEditCellView() ?order list("fingers"))')
  ```

  **关键：** PDK 器件的 `nf` 是只读的。使用 `fingers`：
  ```python
  # ✅ "fingers" 是可编辑的，"nf" 不是
  client.execute_skill(
      'schHiReplace(?replaceAll t ?propName "cellName" ?condOp "==" '
      '?propValue "pch_mac" ?newPropName "fingers" ?newPropValue "4")')

  # ❌ schHiReplace(...?newPropName "nf" ...) → SCH-1725 "not editable"
  ```

  **为什么两步：** `schHiReplace` 更改存储的属性但不触发 CDF 回调。没有回调，派生参数（finger_width、m_ov_nf 注释）保持陈旧。`CCSinvokeCdfCallbacks(?order ...)` 只触发指定的回调，避免来自无关回调的 PDK 错误。

  或者使用处理两步的 Python 包装器：
  ```python
  from virtuoso_bridge.virtuoso.schematic.params import set_instance_params
  set_instance_params(client, "MP0", w="500n", l="30n", nf="4", m="2")
  ```

### 读取设计（原理图 + maestro + 网表）

**始终使用下面的 Python API 函数。不要手写 SKILL 来读取。**

```python
from virtuoso_bridge import VirtuosoClient, decode_skill_output
client = VirtuosoClient.from_env()
LIB, CELL = "myLib", "myCell"

# 1. 原理图 — 默认：仅拓扑（无位置/几何）
from virtuoso_bridge.virtuoso.schematic.reader import read_schematic
data = read_schematic(client, LIB, CELL, include_positions=False)
# data = {
#     "instances": [{"Name", "lib", "cell", "numInst", "view",
#                    "params": {...}, "terms": {...}}, ...],
#     "nets": {"VN1": {"connections": ["M0.D", ...], "numBits": 1,
#                       "sigType": "signal", "isGlobal": false}, ...},
#     "pins": {"VINP": {"direction": "input", "numBits": 1}, ...},
#     "notes": [{"text": "...", ...}, ...]
# }

# 带位置（仅当你需要 xy/bBox 时，例如布局感知编辑）：
data_with_pos = read_schematic(client, LIB, CELL, include_positions=True)

# 不过滤 CDF 参数（返回所有 200+ PDK 参数）：
raw = read_schematic(client, LIB, CELL, include_positions=False, param_filters=None)

# 2. Maestro — 使用 open_session / read_config / close_session
from virtuoso_bridge.virtuoso.maestro import open_session, close_session, read_config
session = open_session(client, LIB, CELL)       # maeOpenSetup（后台，无 GUI）
config = read_config(client, session)            # dict: key -> (skill_expr, raw)
# config keys: maeGetSetup (tests), maeGetEnabledAnalysis, maeGetAnalysis:XXX,
#              maeGetTestOutputs, variables, parameters, corners
close_session(client, session)

# 重要：不要使用 deOpenCellView for maestro — 它打开只读并返回不完整数据。始终使用 open_session (= maeOpenSetup)。

# 3. 网表 — 从 maestro session 生成，通过 SSH 下载
session = open_session(client, LIB, CELL)
test = decode_skill_output(
    client.execute_skill(f'car(maeGetSetup(?session "{session}"))').output)
client.execute_skill(
    f'maeCreateNetlistForCorner("{test}" "Nominal" "/tmp/nl_{CELL}" ?session "{session}")')
client.download_file(f"/tmp/nl_{CELL}/netlist/input.scs", "output/netlist.scs")
close_session(client, session)
```

### 运行仿真

**严格按此顺序执行。不要跳过步骤。**

```python
session = "fnxSession33"  # 从 find_open_session() 或 maeGetSessions() 获取

# 1. 设置变量
client.execute_skill(f'maeSetVar("CL" "1p" ?session "{session}")')

# 2. 运行前保存 — 必须，跳过会导致陈旧状态
client.execute_skill(
    f'maeSaveSetup(?lib "{LIB}" ?cell "{CELL}" ?view "maestro" ?session "{session}")')

# 3. 运行（异步 — 永远不要使用 ?waitUntilDone t，它会死锁事件循环）
r = client.execute_skill(f'maeRunSimulation(?session "{session}")', timeout=30)
history = (r.output or "").strip('"')

# 4. 等待 — 阻塞直到仿真完成（仅 GUI 模式）
r = client.execute_skill("maeWaitUntilDone('All)", timeout=300)

# 5. 检查 GUI 对话框阻塞 — 如果等待返回空/nil，对话框阻塞了 CIW。尝试关闭它：
if not r.output or r.output.strip() in ("", "nil"):
    client.execute_skill("hiFormDone(hiGetCurrentForm())", timeout=5)
    # 如果仍然卡住，用户必须手动在 Virtuoso 中关闭对话框

# 6. 读取结果
client.execute_skill(f'maeOpenResults(?history "{history}")', timeout=15)
r = client.execute_skill(f'maeGetOutputValue("myOutput" "myTest")', timeout=30)
value = float(r.output) if r.output else None
client.execute_skill("maeCloseResults()", timeout=10)
```

### 输出读取/导出保护（碰撞安全）

每当读取或导出**任何** maestro 输出（标量或波形）时应用这些规则：

1. **历史绑定是强制的**
    - 始终使用 `maeRunSimulation()` 返回的精确 `history`。
    - 将该 `history` 明确传递给结果读取器/导出器（例如，`read_results(..., history=history)` 和 `export_waveform(..., history=history)`）。
    - 当需要可重复性时，不要依赖"最新"历史推断。

2. **远程文件名必须唯一**
    - 永远不要使用固定的 `/tmp/vb_wave_xxx.txt` 路径。
    - 使用唯一命名如 `/tmp/vb_wave_<history>_<timestamp>_<nonce>.txt`。
    - 这避免与先前运行或其他用户的陈旧文件冲突。

3. **在 ocnPrint 之前将结果目录绑定到相同的历史**
    - 在 `maeOpenResults(?history ...)` 之后，验证解析的 `resultsDir` 包含 `/<history>/`。
    - 如果检测到不匹配，停止并抛出错误，而不是导出错误的波形。

**在优化循环中：** 在每次迭代中添加 `maeSaveSetup` 和对话框恢复。GUI 对话框（"指定历史名称"、"未启用分析"）阻塞整个 SKILL 通道——所有后续 `execute_skill` 调用将超时，直到对话框被关闭。

**用截图调试：** 如果仿真似乎卡住或结果出乎意料，捕获 Maestro 窗口以查看其当前状态：

```python
client.execute_skill('''
hiWindowSaveImage(
    ?target hiGetCurrentWindow()
    ?path "/tmp/debug_maestro.png"
    ?format "png"
    ?toplevel t
)
''')
client.download_file("/tmp/debug_maestro.png", "output/debug_maestro.png")
```

这揭示了仅通过 SKILL 通道看不到的对话框、错误消息或意外变量值。

### SKILL 通道超时 — 诊断和恢复

当 `execute_skill()` 超时时，可能的原因：

| 原因 | 症状 | 修复 |
|------|------|------|
| **模态对话框** | GUI 弹出阻塞 CIW | `virtuoso-bridge dismiss-dialog` |
| **长时间操作** | 仿真或网表正在运行 | 等待，或使用 `?waitUntilDone nil` |
| **CIW 输入提示** | CIW 等待键入输入 | `dismiss-dialog`（发送 Enter） |
| **桥接断开** | 所有调用立即失败 | `virtuoso-bridge restart` |

**对话框恢复（绕过 SKILL，直接使用 X11）：**

```bash
# 查找并关闭所有阻塞的 Virtuoso 对话框
virtuoso-bridge dismiss-dialog

# 从 Python
client.dismiss_dialog()
```

使用 `xwininfo` 查找 virtuoso 拥有的对话框窗口，使用 `XTestFakeKeyEvent` 发送 Enter。即使 SKILL 通道完全卡住也能工作。

**预防：** 在 `hiCloseWindow(win)` 之前始终 `dbSave(cv)`。永远不要在仿真调用中使用 `?waitUntilDone t`。在仿真循环中添加对话框恢复（参见"运行仿真"部分）。

## 相关 skills

- **spectre** — 独立网表驱动的 Spectre 仿真（无需 Virtuoso GUI）。当用户有 `.scs` 网表并想直接运行时使用。
