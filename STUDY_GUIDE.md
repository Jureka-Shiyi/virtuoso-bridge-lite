# virtuoso-bridge-lite 系统学习指南

本文档提供从入门到精通的完整学习路径，帮助你系统掌握本项目的全部代码。

---

## 📋 学习路线图

```
阶段1: 基础概念 (2-3天)
    │
    ▼
阶段2: 核心机制 - core/ (3-5天)
    │
    ▼
阶段3: 传输层 - transport/ (2-3天)
    │
    ▼
阶段4: Virtuoso客户端 - virtuoso/ (5-7天)
    │
    ▼
阶段5: Spectre仿真 - spectre/ (3-4天)
    │
    ▼
阶段6: 进阶实战 (持续)
```

---

## 阶段1: 基础概念与环境准备

### 学习目标
- 理解项目架构和设计理念
- 搭建开发环境
- 掌握 SKILL 语言基础
- 了解 Cadence Virtuoso 基本概念

### 学习资料

#### 1.1 项目文档阅读
| 文档 | 内容 | 预计时间 |
|------|------|----------|
| `README.md` | 项目介绍、架构概览、快速开始 | 30分钟 |
| `AGENTS.md` | 详细设置指南、关键约定 | 1小时 |
| `core/README.md` | 核心机制说明 | 30分钟 |
| `PROJECT_STRUCTURE.md` | 项目结构总览 | 20分钟 |

#### 1.2 前置知识学习

**Cadence Virtuoso 基础**
- 了解 Virtuoso 的基本界面（CIW、Library Manager、Schematic Editor、Layout Editor）
- 学习 Library/Cell/View 的概念
- 推荐资源：Cadence 官方文档或大学 EDA 课程

**SKILL 语言基础**
```skill
; 基本语法学习清单
1. 变量定义: x = 5, let((x 5) ...)
2. 函数定义: procedure(myFunc(arg) ...)
3. 列表操作: list(1 2 3), car(), cdr(), cons()
4. 条件判断: if/then/else, when, unless
5. 循环: foreach, while
6. 对象访问: obj~>property
7. 数据库操作: dbOpenCellViewByType, ddGetObj
```

**推荐学习资源**
- [SKILL 语言参考](https://support.cadence.com/)
- `examples/01_virtuoso/assets/` 中的示例脚本

#### 1.3 环境搭建实践
```bash
# 1. 克隆项目
git clone <repo-url>
cd virtuoso-bridge-lite

# 2. 创建虚拟环境
uv venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 3. 安装项目
uv pip install -e ".[dev]"

# 4. 验证安装
virtuoso-bridge --help
```

### 实践练习
1. [ ] 成功运行 `virtuoso-bridge init` 并配置 `.env`
2. [ ] 连接远程 Virtuoso，执行 `1+2` 并获取结果
3. [ ] 在 CIW 中手动执行几个简单的 SKILL 命令

---

## 阶段2: 核心机制理解 (core/)

### 学习目标
- 深入理解 IPC 通信机制
- 掌握守护进程的工作原理
- 理解 SKILL-Python 桥接协议
- 能够独立搭建最小化桥接系统

### 学习资料

#### 2.1 文件阅读顺序

**第1步: ramic_bridge.il (SKILL 端)**
```
学习内容:
├── ipcBeginProcess() 函数
├── 回调机制 (RBIpcDataHandler)
├── 错误处理 (errset)
├── 进程生命周期管理
└── 协议设计 (STX/NAK/RS)
```

**关键问题思考:**
1. 为什么使用 `ipcBeginProcess` 而不是其他通信方式？
2. `errset` 的作用是什么？如果没有它会怎样？
3. 为什么选择 `\x02` 和 `\x15` 作为状态标记？
4. 环境变量清除 (`env -u`) 的必要性是什么？

**第2步: ramic_daemon.py (守护进程)**
```
学习内容:
├── 非阻塞 I/O (fcntl)
├── 协议解析 (read_result)
├── 安全检查 (_check_skill)
├── 多行 SKILL 处理
└── TCP 服务器实现
```

**关键问题思考:**
1. 为什么需要将 stdin 设为非阻塞模式？
2. 安全过滤器的正则表达式如何工作？
3. 如何处理多行 SKILL 代码？
4. 为什么是单线程设计？优缺点是什么？

**第3步: bridge_client.py (客户端)**
```
学习内容:
├── TCP 客户端实现
├── JSON 协议
├── 响应解析
└── 错误处理
```

**关键问题思考:**
1. 为什么使用 JSON 作为请求格式？
2. `socket.shutdown(SHUT_WR)` 的作用是什么？
3. 如何处理部分接收的数据？

#### 2.2 扩展阅读

**通信协议详解**
```
协议栈:
┌─────────────────────────────────────┐
│  Application: SKILL/Python JSON      │
├─────────────────────────────────────┤
│  Transport: TCP Socket               │
├─────────────────────────────────────┤
│  Network: SSH Tunnel (optional)      │
├─────────────────────────────────────┤
│  IPC: stdin/stdout (daemon↔Virtuoso) │
└─────────────────────────────────────┘

数据包格式:
请求:  {"skill": "1+2", "timeout": 30}
响应:  \x02"3"\x1e  (成功) 或  \x15"error"\x1e  (失败)
```

### 实践练习

#### 练习 2.1: 修改端口号
```python
# 修改 ramic_bridge.il 中的 RBPort
# 修改 ramic_daemon.py 的默认端口
# 测试连接是否成功
```

#### 练习 2.2: 添加新的安全检查
```python
# 在 _BLOCKED_FNS 中添加更多危险函数
# 测试是否能正确拦截
_BLOCKED_FNS = re.compile(
    r'(?<!["\w])(shell|system|ipcBeginProcess|getShellEnvVar|'
    r'ssh|telnet|wget|curl)\s*\(',
)
```

#### 练习 2.3: 实现心跳机制
```python
# 在 ramic_daemon.py 中添加心跳检测
# 如果长时间无响应，自动重启连接
```

#### 练习 2.4: 调试模式
```python
# 添加 --debug 参数
# 打印所有收发的数据
# 记录到日志文件
```

### 验证标准
- [ ] 能够解释完整的数据流（从 Python 到 Virtuoso 再返回）
- [ ] 能够手绘架构图
- [ ] 能够修改并测试核心组件
- [ ] 能够诊断基本的连接问题

---

## 阶段3: 传输层 (transport/)

### 学习目标
- 理解 SSH 隧道的工作原理
- 掌握远程文件传输
- 理解 ControlMaster 连接复用
- 能够配置多服务器环境

### 学习资料

#### 3.1 文件阅读顺序

**ssh.py**
```python
# 重点类: SSHClient
核心功能:
- 建立 SSH 连接
- 执行远程命令
- 端口转发 (tunnel)
- 文件传输 (rsync/scp)

关键方法:
├── from_env()      # 从环境变量创建
├── warm()          # 预热连接
├── execute()       # 执行远程命令
├── upload/download # 文件传输
└── check_spectre() # 检查 Spectre 可用性
```

**tunnel.py**
```python
# 重点: SSH 隧道管理
核心功能:
- 建立端口转发
- 自动重连
- 多路复用
- 状态监控

关键概念:
├── ControlMaster   # SSH 连接复用
├── -L 端口转发     # 本地到远程
├── -J 跳板主机     # Jump host
└── 配置文件解析    # ~/.ssh/config
```

**remote_paths.py**
```python
# 远程路径管理
功能:
- 路径规范化
- 临时目录管理
- 权限处理
```

#### 3.2 SSH 相关知识

**必须掌握的 SSH 概念**
```bash
# 1. 基本连接
ssh user@host

# 2. 端口转发
ssh -L 本地端口:目标主机:目标端口 user@跳板

# 3. ControlMaster（连接复用）
ssh -M -S ~/.ssh/control-%r@%h:%p user@host
ssh -S ~/.ssh/control-%r@%h:%p -O check user@host

# 4. 跳板主机
ssh -J jump-host target-host

# 5. 配置 ~/.ssh/config
Host my-server
    HostName 192.168.1.100
    User myuser
    IdentityFile ~/.ssh/id_rsa
```

### 实践练习

#### 练习 3.1: 手动建立 SSH 隧道
```bash
# 1. 手动建立隧道
ssh -N -L 65432:localhost:65432 my-server

# 2. 使用 bridge_client.py 测试连接
python core/bridge_client.py '1+2'

# 3. 检查连接状态
ssh -O check my-server
```

#### 练习 3.2: 多服务器配置
```python
# 配置 .env 支持两台服务器
VB_REMOTE_HOST=server-a
VB_REMOTE_USER=user-a
VB_REMOTE_HOST_worker1=server-b
VB_REMOTE_USER_worker1=user-b

# 测试多配置
virtuoso-bridge start -p worker1
virtuoso-bridge status -p worker1
```

#### 练习 3.3: 文件传输测试
```python
from virtuoso_bridge.transport.ssh import SSHClient

client = SSHClient.from_env()

# 上传文件
client.upload_file("local.txt", "/tmp/remote.txt")

# 下载文件
client.download_file("/tmp/remote.txt", "downloaded.txt")

# 执行命令
result = client.execute("ls -la /tmp/")
print(result.stdout)
```

### 验证标准
- [ ] 理解 ControlMaster 的工作原理
- [ ] 能够手动建立 SSH 隧道
- [ ] 能够配置多服务器环境
- [ ] 能够实现自定义文件传输

---

## 阶段4: Virtuoso客户端 (virtuoso/)

### 学习目标
- 掌握 VirtuosoClient 的使用
- 理解 layout/schematic/maestro 三大模块
- 能够编写自动化设计脚本
- 掌握错误处理和调试技巧

### 学习资料

#### 4.1 模块结构

```
virtuoso/
├── basic/          # 基础客户端
│   ├── bridge.py   # VirtuosoClient 主类
│   └── composition.py
├── layout/         # 版图编辑
│   ├── editor.py   # LayoutEditor 上下文管理器
│   ├── ops.py      # 版图操作
│   └── reader.py   # 版图读取
├── schematic/      # 原理图编辑
│   ├── editor.py   # SchematicEditor
│   ├── ops.py      # 原理图操作
│   ├── reader.py   # 连接关系读取
│   └── params.py   # CDF参数设置
└── maestro/        # 仿真配置
    ├── session.py  # 会话管理
    ├── reader.py   # 配置读取
    └── writer.py   # 配置写入
```

#### 4.2 学习顺序

**第1步: basic/bridge.py - VirtuosoClient**
```python
# 核心功能:
├── execute_skill()   # 执行原始 SKILL
├── load_il()         # 加载 .il 文件
├── open_window()     # 打开窗口
├── layout.edit()     # 版图编辑上下文
├── schematic.edit()  # 原理图编辑上下文
└── 文件操作 (upload/download)

# 使用模式:
from virtuoso_bridge import VirtuosoClient

client = VirtuosoClient.from_env()  # 从环境变量
# 或
client = VirtuosoClient.local(port=65432)  # 本地模式
```

**第2步: layout/ - 版图编辑**
```python
# 核心概念:
├── LayoutEditor  # 上下文管理器 (with语句)
├── LayoutOps     # 操作队列
├── 基本形状: rect, path, polygon, label
├── 实例化: instance (MOS, 电容等)
└── 技术信息: layer/purpose

# 示例学习:
examples/01_virtuoso/layout/
├── 01_create_layout.py      # 基础创建
├── 02_add_polygon.py        # 多边形
├── 03_add_via.py            # 通孔
├── 04_multilayer_routing.py # 多层布线
└── 06_read_layout.py        # 读取版图
```

**第3步: schematic/ - 原理图编辑**
```python
# 核心概念:
├── SchematicEditor  # 上下文管理器
├── 实例化: instance
├── 连线: wire, net label
├── 引脚: pin
├── 参数: CDF params
└── 连接关系: connectivity

# 示例学习:
examples/01_virtuoso/schematic/
├── 01a_create_rc_stepwise.py  # 分步创建
├── 02_read_connectivity.py    # 读取连接
├── 03_read_instance_params.py # 读取参数
└── 08_import_cdl_cap_array.py # CDL导入
```

**第4步: maestro/ - 仿真配置**
```python
# 核心概念:
├── Session  # Maestro 会话
├── Test     # 测试用例
├── Corner   # 工艺角
├── Analysis # 分析类型 (tran/ac/dc)
├── Variable # 变量
└── Output   # 输出信号

# 示例学习:
examples/01_virtuoso/maestro/
├── 01_read_open_maestro.py    # 读取配置
├── 04_read_env.py             # 环境设置
├── 05_read_results.py         # 读取结果
└── 06b_rc_simulate_and_read.py # 运行仿真
```

#### 4.3 重要 SKILL 函数参考

```skill
; 数据库操作
dbOpenCellViewByType(lib cell view "maskLayout")  ; 打开版图
dbOpenCellViewByType(lib cell view "schematic")   ; 打开原理图
ddGetObj(lib cell)                                 ; 获取对象
ddDeleteObj(obj)                                   ; 删除对象

; 版图操作
dbCreateRect(cv layer bbox)                        ; 创建矩形
dbCreatePath(cv layer points width)                ; 创建路径
dbCreateInst(cv master nil xy orient)              ; 创建实例
dbCreateLabel(cv layer text xy orient height)      ; 创建标签

; 原理图操作
schCreateInst(cv master xy orient)                 ; 创建实例
schCreateWire(cv points width)                     ; 创建连线
schCreatePin(cv name direction xy orient)          ; 创建引脚

; Maestro 操作
maeOpenSetup(lib cell view "maestro")              ; 打开 Maestro
maeRunSimulation(?session session)                 ; 运行仿真
maeGetOutputValue(output test)                     ; 获取输出值
```

### 实践练习

#### 练习 4.1: 创建简单反相器原理图
```python
# 目标: 使用 Python API 创建一个 CMOS 反相器原理图

from virtuoso_bridge import VirtuosoClient
from virtuoso_bridge.virtuoso.schematic import (
    schematic_create_inst_by_master_name as inst,
    schematic_create_pin as pin,
)

client = VirtuosoClient.from_env()

with client.schematic.edit("myLib", "inv") as sch:
    # 添加 PMOS 和 NMOS
    sch.add(inst("tsmcN28", "pch_mac", "symbol", "MP0", 0, 1.5, "R0"))
    sch.add(inst("tsmcN28", "nch_mac", "symbol", "MN0", 0, 0, "R0"))
    
    # 添加引脚
    sch.add(pin("IN", 0, 0.75, "R0", direction="input"))
    sch.add(pin("OUT", 2, 0.75, "R0", direction="output"))
    sch.add(pin("VDD", 0.5, 2, "R0", direction="inputOutput"))
    sch.add(pin("VSS", 0.5, -0.5, "R0", direction="inputOutput"))

client.open_window("myLib", "inv", view="schematic")
```

#### 练习 4.2: 版图布局自动化
```python
# 目标: 创建一个简单的电容阵列版图

from virtuoso_bridge.virtuoso.layout.ops import (
    layout_create_param_inst as inst,
    layout_create_rect as rect,
)

with client.layout.edit("myLib", "cap_array") as layout:
    # 创建 2x2 电容阵列
    for i in range(2):
        for j in range(2):
            x, y = i * 5.0, j * 5.0
            layout.add(inst("tsmcN28", "cfmom_2t", "layout", 
                           f"C{i}{j}", x, y, "R0"))
            # 添加金属线
            layout.add(rect("M1", "drawing", x+1, y+1, x+4, y+4))
```

#### 练习 4.3: 读取并分析设计
```python
# 目标: 读取原理图并分析连接关系

from virtuoso_bridge.virtuoso.schematic.reader import read_schematic

data = read_schematic(client, "myLib", "inv")

print("实例列表:")
for inst in data["instances"]:
    print(f"  {inst['name']}: {inst['lib']}/{inst['cell']}")

print("\n网络列表:")
for net_name, net_data in data["nets"].items():
    print(f"  {net_name}: {net_data['connections']}")
```

#### 练习 4.4: Maestro 自动化仿真
```python
# 目标: 设置并运行一次完整的仿真

from virtuoso_bridge.virtuoso.maestro import (
    open_session, close_session, read_config
)

# 打开会话
session = open_session(client, "myLib", "inv_tb")

# 读取当前配置
config = read_config(client, session)
print(f"测试: {config.get('tests', [])}")
print(f"分析: {config.get('analyses', [])}")

# 设置变量
client.execute_skill(f'maeSetVar("VDD" "0.8" ?session "{session}")')

# 保存并运行
client.execute_skill(
    f'maeSaveSetup(?lib "myLib" ?cell "inv_tb" ?view "maestro" ?session "{session}")'
)
history = client.execute_skill(
    f'maeRunSimulation(?session "{session}")'
).output

# 等待完成
client.execute_skill("maeWaitUntilDone('All)", timeout=300)

# 读取结果
result = client.execute_skill(
    f'maeGetOutputValue("delay" "tran")'
)
print(f"延迟: {result.output}")

# 关闭会话
close_session(client, session)
```

### 验证标准
- [ ] 能够创建和编辑原理图
- [ ] 能够创建和编辑版图
- [ ] 能够读取设计信息并分析
- [ ] 能够配置和运行 Maestro 仿真
- [ ] 理解所有模块的设计模式

---

## 阶段5: Spectre仿真 (spectre/)

### 学习目标
- 理解 Spectre 仿真流程
- 掌握网表格式和语法
- 能够解析 PSF 结果
- 实现批量仿真

### 学习资料

#### 5.1 模块结构

```python
spectre/
├── runner.py    # SpectreSimulator 类
└── parsers.py   # PSF 结果解析
```

#### 5.2 核心概念

**Spectre 仿真流程**
```
本地网文件 (.scs)
      │
      ▼
[上传] ───────► 远程服务器
      │
      ▼
运行 Spectre
      │
      ▼
[下载] ◄─────── 结果 (.raw)
      │
      ▼
解析 PSF ◄───── 波形数据
```

**网表基本结构**
```spice
* 标题
include "/path/to/model.scs" section=tt

* 子电路定义
subckt inverter in out vdd vss
    mp (out in vdd vdd) pch l=30n w=1u
    mn (out in vss vss) nch l=30n w=500n
ends

* 测试平台
vin (in 0) vsource type=pulse val0=0 val1=0.8 period=10n
vvd (vdd 0) vsource dc=0.8
vvs (vss 0) vsource dc=0

* 实例化
xinv (in out vdd vss) inverter

* 分析语句
tran tran stop=50n errpreset=conservative
save xinv:out
```

### 实践练习

#### 练习 5.1: 简单瞬态仿真
```python
# 创建网表
netlist = '''
simulator lang=spectre

vin (in 0) vsource type=dc dc=1.0
r1 (in out) resistor r=1k
c1 (out 0) capacitor c=1p

dc dc
save in out
'''

# 写入文件
with open("rc.scs", "w") as f:
    f.write(netlist)

# 运行仿真
from virtuoso_bridge.spectre import SpectreSimulator, spectre_mode_args

sim = SpectreSimulator.from_env(
    spectre_args=spectre_mode_args("spectre"),
    work_dir="./output"
)

result = sim.run_simulation("rc.scs", {})

if result.ok:
    print(f"电压: {result.data['out']}")
else:
    print(f"错误: {result.errors}")
```

#### 练习 5.2: 批量仿真
```python
# 参数扫描
import numpy as np

resistors = np.linspace(1e3, 10e3, 10)
tasks = []

for r in resistors:
    # 为每个参数创建网表
    netlist = f'''
    vin (in 0) vsource type=dc dc=1.0
    r1 (in out) resistor r={r}
    c1 (out 0) capacitor c=1p
    dc dc
    '''
    netlist_file = f"rc_{r}.scs"
    with open(netlist_file, "w") as f:
        f.write(netlist)
    
    # 提交任务
    task = sim.submit(Path(netlist_file))
    tasks.append((r, task))

# 收集结果
for r, task in tasks:
    result = task.result()
    if result.ok:
        vout = result.data['out'][0]
        print(f"R={r:.0f}, Vout={vout:.4f}")
```

#### 练习 5.3: 自定义解析
```python
from virtuoso_bridge.spectre.parsers import parse_psf

# 手动解析 PSF 文件
with open("output/raw/tran.tran.tran", "rb") as f:
    data = parse_psf(f)

# 分析波形
time = data["time"]
vout = data["out"]

# 计算延迟
import numpy as np
threshold = 0.4
idx = np.where(np.diff(np.sign(vout - threshold)))[0]
delay = time[idx[0]]
print(f"延迟: {delay * 1e12:.2f} ps")
```

### 验证标准
- [ ] 理解 Spectre 网表语法
- [ ] 能够运行独立仿真（不依赖 Virtuoso GUI）
- [ ] 能够批量运行并行仿真
- [ ] 能够解析和处理仿真结果

---

## 阶段6: 进阶实战

### 6.1 技能文件开发

学习如何编写和扩展技能文件：

```markdown
skills/
├── virtuoso/SKILL.md      # 主技能文档
├── virtuoso/references/    # API 参考
└── spectre/SKILL.md        # Spectre 技能

技能文件格式:
---
name: skill-name
description: "技能描述"
---

# 标题

## 章节
- 列表项
- 代码示例
```

### 6.2 项目实践建议

**项目 1: 自动化标准单元库**
- 创建标准单元（反相器、与非门、或非门等）
- 自动生成原理图和版图
- 批量仿真验证
- 生成 Liberty 时序文件

**项目 2: 参数化 IP 生成器**
- 设计可配置的放大器/比较器
- 参数化版图生成
- 自动匹配和布线
- 仿真验证自动化

**项目 3: 设计迁移工具**
- 从一个 PDK 迁移到另一个 PDK
- 自动替换器件模型
- 重新仿真验证
- 版图适配

### 6.3 性能优化

```python
# 1. 批量操作替代单个操作
# ❌ 低效: 多次 execute_skill
for i in range(100):
    client.execute_skill(f'dbCreateRect(cv "M1" list(0:{i} 10:{i+1}))')

# ✅ 高效: 一次性发送
skill_code = '''
let((cv cv=geGetEditCellView())
  for(i 0 99
    dbCreateRect(cv "M1" list(0:i 10:i+1))
  )
)
'''
client.execute_skill(skill_code)

# 2. 使用上下文管理器
# 自动保存和关闭
with client.layout.edit(lib, cell) as layout:
    # 批量添加形状
    pass  # 自动保存

# 3. 并行仿真
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=4) as executor:
    futures = [executor.submit(run_sim, cfg) for cfg in configs]
```

### 6.4 调试技巧

```python
# 1. 启用调试日志
import logging
logging.basicConfig(level=logging.DEBUG)

# 2. 截图调试
client.execute_skill('''
hiWindowSaveImage(
    ?target hiGetCurrentWindow()
    ?path "/tmp/debug.png"
    ?format "png"
)
''')
client.download_file("/tmp/debug.png", "debug.png")

# 3. SKILL 代码检查
# 在 CIW 中手动测试
# 使用 printf 打印中间结果

# 4. 超时处理
from virtuoso_bridge.models import VirtuosoResult

try:
    result = client.execute_skill("long_operation()", timeout=60)
except TimeoutError:
    # 尝试恢复
    client.execute_skill("hiFormDone(hiGetCurrentForm())")
```

---

## 📚 参考资源

### 官方文档
- [Cadence SKILL 参考](https://support.cadence.com/)
- [Spectre 电路仿真器参考](https://support.cadence.com/)
- [Python 3 文档](https://docs.python.org/3/)

### 项目内部资源
```
必读的示例:
├── examples/01_virtuoso/basic/00_ciw_output_vs_return.py
├── examples/01_virtuoso/schematic/01a_create_rc_stepwise.py
├── examples/01_virtuoso/layout/01_create_layout.py
└── examples/02_spectre/01_inverter_tran.py

必读的参考:
├── skills/virtuoso/references/schematic-python-api.md
├── skills/virtuoso/references/layout-python-api.md
└── skills/virtuoso/references/troubleshooting.md
```

### 推荐工具
- **代码编辑器**: VS Code + Python 扩展
- **SSH 客户端**: Windows Terminal / iTerm2 / Terminal
- **Python 环境**: uv (推荐) 或 conda
- **版本控制**: Git

---

## ✅ 学习检查清单

### 基础阶段
- [ ] 理解项目架构
- [ ] 成功安装并运行项目
- [ ] 能够执行简单的 SKILL 命令
- [ ] 理解 Library/Cell/View 概念

### 核心机制
- [ ] 能够解释完整的数据流
- [ ] 理解 IPC 通信机制
- [ ] 能够修改核心组件
- [ ] 理解安全过滤机制

### 传输层
- [ ] 理解 SSH 隧道原理
- [ ] 能够配置多服务器
- [ ] 掌握文件传输

### Virtuoso 客户端
- [ ] 能够创建原理图
- [ ] 能够创建版图
- [ ] 能够读取设计信息
- [ ] 能够配置 Maestro 仿真

### Spectre 仿真
- [ ] 理解网表格式
- [ ] 能够运行独立仿真
- [ ] 能够批量并行仿真
- [ ] 能够解析结果

### 进阶
- [ ] 完成至少一个实战项目
- [ ] 能够诊断和解决问题
- [ ] 能够扩展功能

---

## 🎯 学习建议

1. **循序渐进**: 不要跳过阶段，每个阶段都是下一个的基础
2. **动手实践**: 只看不做等于没学，每个阶段都要完成练习
3. **遇到问题先查**: 养成查文档和参考的习惯
4. **做笔记**: 记录遇到的问题和解决方案
5. **分享交流**: 和同事或社区讨论，加深理解

---

## 💡 常见问题 (FAQ)

**Q: 没有 Virtuoso 许可证可以学习吗？**
A: 可以学习代码结构和 Python 部分，但无法实际运行测试。

**Q: SKILL 语言难学吗？**
A: 对于 Lisp/Scheme 有经验的会比较容易，否则需要 1-2 周适应。

**Q: 需要硬件知识吗？**
A: 基础了解即可，重点是理解 EDA 工具的自动化接口。

**Q: 学习周期大概多久？**
A: 全职学习约 2-3 周可达到独立开发水平，兼职约 2 个月。

---

*本学习指南由 AI 生成，可根据个人情况调整学习进度。*

**最后更新**: 2026-04-11
