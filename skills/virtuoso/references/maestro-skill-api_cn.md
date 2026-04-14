# Maestro SKILL API 参考

## 两种会话模式

| | 后台（`maeOpenSetup`） | GUI（`deOpenCellView`） |
|---|---|---|
| 锁文件 | 创建 `.cdslck` | 创建 `.cdslck` |
| 读取配置 | 是 | 是 |
| 写入配置 | 是 | 是（需要 `maeMakeEditable`） |
| 运行仿真 | 可以启动，但 `maeCloseSession` 会取消 | 是 |
| `maeWaitUntilDone` | 立即返回（不等待） | 阻塞直到完成 |
| 关闭 | `maeCloseSession` → 锁删除 | `hiCloseWindow` → 可能触发对话框 |
| 崩溃残留 | 锁文件保留 | 锁文件保留 |

**经验法则：后台用于读取/写入配置，GUI 用于仿真。**

残留锁清理：首先对任何陈旧会话（`maeGetSessions`）尝试 `maeCloseSession`。只有在没有活动会话时（例如 Virtuoso 崩溃后）才手动删除 `.cdslck`。

---

## 目录

1. [支持的 ADE 类型](#支持的-ade-类型)
2. [设计变量](#设计变量)
3. [Maestro mae* API](#maestro-mae-api-ic618--ic231)——会话管理、读取设置、创建测试、分析配置、输出、变量、corners、环境选项、保存、运行、读取结果、历史显示、工具函数
4. [已知阻塞因素](#已知阻塞因素)——GUI 对话框、原理图检查、编辑锁
5. [Pnoise Jitter Event——自动化限制](#pnoise-jitter-event——自动化限制)
6. [读取结果——OCEAN API](#读取结果——ocean-api)
7. [OCEAN 快速参考](#ocean-快速参考)
8. [完整 Maestro 工作流程（Python）](#完整-maestro 工作流程-python)
9. [Maestro SKILL 工具函数](#maestro-skill-工具函数)
10. [示例](#示例)

---

## 支持的 ADE 类型

| 类型 | 运行函数 | 会话访问 |
|------|-------------|----------------|
| **ADE Assembler（Maestro）** | `maeRunSimulation()` | `maeOpenSetup(lib cell "maestro")` |
| **ADE Explorer** | `sevRun(sevSession(win))` | `sevSession(win)` |

**关键：** `sevRun` 不适用于 ADE Assembler——`sevSession()` 在 Assembler 窗口上返回 nil。

## asi\* 旧版 Virtuoso 环境回退

在旧版 Virtuoso（IC6.1.8 之前或某些学术版）中，`mae*` 函数可能不可用（`*Error* undefined function`）。`asi*` API 覆盖相同功能且适用于所有 ADE 类型：

| mae\*（IC618+） | asi\* 等效 | 备注 |
|----------------|-----------------|------|
| `maeOpenSetup(lib cell "maestro")` | `asiOpenSetup(lib cell "maestro")` | 返回会话句柄 |
| `maeGetSessions()` | `asiGetSessionList()` | 列出打开的会话 |
| `maeGetVar("VDD")` | `asiGetDesignVarList(asiGetCurrentSession())` | 以列表形式返回所有变量 |
| `maeSetVar("VDD" "0.9")` | `asiSetDesignVarValue(asiGetCurrentSession() "VDD" "0.9")` | |
| `maeRunSimulation()` | `asiRunSimulation()` | |
| `maeWaitUntilDone('All)` | — | 无直接等效；用 `asiGetStatus()` 轮询 |
| `maeGetOutputValue(...)` | 使用 OCEAN（`openResults` / `evalOutput`） | 见下文 OCEAN 部分 |
| `maeCloseSession(session)` | `asiCloseSession(asiGetCurrentSession())` | |

**检测：** 运行时检查再选择路径：
```scheme
if(fboundp('maeRunSimulation)
  then /* mae* 流程 */
  else /* asi* 回退 */
)
```

使用 `asi*` 时，通过 OCEAN（`openResults` / `selectResult` / `getData`）读取仿真结果——见下面的 [OCEAN 快速参考](#ocean-快速参考)。

## 设计变量

```python
# 列出所有全局变量
client.execute_skill('maeGetSetup(?typeName "globalVar")')

# 获取 / 设置
client.execute_skill('maeGetVar("VDD")')
client.execute_skill('maeSetVar("VDD" "0.85")')

# 参数扫描（逗号分隔）
client.execute_skill('maeSetVar("VDD" "0.8,0.9,1.0")')
```

## Maestro mae* API（IC618 / IC231）

所有 `mae*` 函数操作**完整的 maestro cellview**，不仅仅是可见窗口。如果 maestro 在 GUI 中打开，`?session` 可以省略。

### 会话管理

```scheme
; 打开现有的 maestro（返回会话字符串，例如 "fnxSession4"）
session = maeOpenSetup("myLib" "myCell" "maestro")

; 以追加模式打开（用于编辑现有设置）
session = maeOpenSetup("myLib" "myCell" "maestro" ?mode "a")
```

**`?session` 是一个字符串。** 传递为 `?session "fnxSession4"`，而不是未加引号的变量。

### 读取现有设置

读取打开的 Maestro 会话的完整配置。**必须首先通过 `deOpenCellView` 打开 GUI**，然后调用 `maeGetSetup()` 不带 `?typeName` 以获取测试列表。

```scheme
; 测试列表
maeGetSetup()                              ; => ("tb_cmp_SA")

; 测试的启用分析
maeGetEnabledAnalysis("tb_cmp_SA")         ; => ("pss" "pnoise")

; 分析参数（返回所有选项键值对）
maeGetAnalysis("tb_cmp_SA" "pss")
; => (("fund" "1G") ("harms" "10") ("errpreset" "conservative") ...)

maeGetAnalysis("tb_cmp_SA" "pnoise")
; => (("fund" "1G") ("start" "0") ("stop" "500M") ...)

; 设计变量（使用 asi* API，不是 maeGetSetup）
asiGetDesignVarList(asiGetCurrentSession())
; => (("VDD" "0.81:0.09:0.99") ("Vcm" "0.475") ...)

; 输出——返回 sevOutputStruct 列表，用 nth/~>name 遍历
maeGetTestOutputs("tb_cmp_SA")
; 访问：nth(0 outputs)~>name, ~>outputType, ~>signalName, ~>expr

; 仿真器名称
maeGetEnvOption("tb_cmp_SA" ?option "simExecName")  ; => "spectre"

; 模型文件
maeGetEnvOption("tb_cmp_SA" ?option "modelFiles")
; => (("/path/to/model.scs" "tt") ("/path/to/model.scs" "ss") ...)

; 运行模式
maeGetCurrentRunMode()  ; => "Single Run, Sweeps and Corners"
```

**注意：** `maeGetSetup(?typeName "globalVar")` 即使存在变量也可能返回 nil。使用 `asiGetDesignVarList(asiGetCurrentSession())` 代替以可靠地读取设计变量。

### 创建测试

```scheme
; 创建新测试（如果在 GUI 中 maestro 打开，session 可选）
maeCreateTest("AC" ?lib "myLib" ?cell "myCell"
  ?view "schematic" ?simulator "spectre" ?session "fnxSession4")

; 从现有测试复制
maeCreateTest("TRAN2" ?sourceTest "TRAN" ?session "fnxSession4")
```

### 分析配置

选项使用**反引号引用的** SKILL 列表语法：

```scheme
; AC 分析
maeSetAnalysis("AC" "ac" ?enable t ?options
  `(("start" "1") ("stop" "10G") ("incrType" "Logarithmic")
    ("stepTypeLog" "Points Per Decade") ("dec" "20")))

; Transient
maeSetAnalysis("TRAN" "tran" ?enable t ?options
  `(("stop" "60n") ("errpreset" "conservative")))

; DC 工作点
maeSetAnalysis("TRAN" "dc" ?enable t ?options `(("saveOppoint" t)))

; 禁用分析
maeSetAnalysis("AC" "tran" ?enable nil)

; 检查分析设置
maeGetAnalysis("AC" "ac")
; => (("anaName" "ac") ("sweep" "Frequency") ("start" "1") ("stop" "10G") ...)
```

### 输出

```scheme
; 信号输出（波形）
maeAddOutput("OutPlot" "TRAN" ?outputType "net" ?signalName "/OUT")

; 表达式输出（标量）
maeAddOutput("maxOut" "TRAN" ?outputType "point" ?expr "ymax(VT(\"/OUT\"))")

; 带宽测量（-3 dB）
; 注意：在 Maestro 输出表达式中使用 VF()（频域电压）而不是 v()
maeAddOutput("BW" "AC" ?outputType "point" ?expr "bandwidth(mag(VF(\"/OUT\")) 3 \"low\")")

; 添加规格（通过/失败检查）
maeSetSpec("maxOut" "TRAN" ?lt "400m")   ; < 400mV
maeSetSpec("BW" "AC" ?gt "1G")           ; > 1 GHz
; 规格操作符：?lt (<)、?gt (>)、?minimum、?maximum、?tolerence
```

### 设计变量

```scheme
; 设置全局变量
maeSetVar("vdd" "1.3")
maeSetVar("vdd" "1.3" ?session "fnxSession4")

; 获取全局变量
maeGetVar("vdd")    ; => "1.3"

; 参数扫描——逗号分隔的值
maeSetVar("c_val" "1p,100f" ?session "fnxSession4")
```

### Corners

Corner 管理的 SKILL API 支持有限。`maeSetCorner` 只能创建/启用/禁用 corners。模型文件和变量必须通过直接编辑 `maestro.sdb` XML 来设置。

#### 读取 corners

Corners 存储在 `maestro.sdb` XML 中。下载并解析：

```python
client.download_file(f'{maestro_dir}/maestro.sdb', '/tmp/maestro.sdb')
# 解析 <corner enabled="1">name ... </corner> 块
# 每个 corner 有：<vars>、<models> 子元素
```

#### 创建 corner（空）

```scheme
; 创建没有 model/var 的 corner——只支持 ?enabled
maeSetCorner("tt_25" ?enabled t)
```

#### 创建带 model + temperature 的 corner

完整 corners（带模型文件和变量）需要编辑 `maestro.sdb` XML。先关闭 maestro 会话，然后在 `</corners>` 前插入 corner XML 块：

```xml
<corner enabled="1">tt_25
    <vars>
        <var>temperature
            <value>25</value>
        </var>
    </vars>
    <models>
        <model enabled="1">toplevel_modified.scs
            <modeltest>All</modeltest>
            <modelblock>Global</modelblock>
            <modelfile>/home/zhangz/T28/toplevel_modified.scs</modelfile>
            <modelsection>"top_tt"</modelsection>
        </model>
    </models>
</corner>
```

插入 corners 的 Python 辅助函数（通过 `upload_file` + `run_shell_command` 在远程运行）：

```python
# 1. 关闭 maestro 会话
client.execute_skill('MaestroClose("myLib" "myCell")')

# 2. 在远程编辑 sdb（上传并执行 python2 脚本）
# 在第一个 </corners> 标签前插入新的 corner XML 块
# 见 edit_sdb.py 模式：读行，在 </corners> 前插入，写回

# 3. 重新打开 maestro 加载更改
client.execute_skill('MaestroOpen("myLib" "myCell")')
```

#### 启用 / 禁用 corner

```scheme
maeSetCorner("tt_25" ?enabled t)    ; 启用
maeSetCorner("tt_25" ?enabled nil)  ; 禁用
```

#### 删除 corner

```scheme
maeDeleteCorner("tt_25")
maeSaveSetup()  ; 持久化删除
```

**注意：** `maeDeleteCorner` 在内存中工作。`maeSaveSetup` 持久化到 sdb。如果 corner 是通过直接 sdb 编辑插入的且没有先重新打开 maestro，删除可能不会生效——sdb 编辑后总是重新打开 maestro 再使用 mae* 函数。

#### 已探索但不支持的关键字

`maeSetCorner` 只接受 `?enabled`。这些关键字**不工作**：
`?temperature`、`?model`、`?modelFile`、`?modelSection`、`?vars`、`?models`、`?varList`、`?file`、`?section`、`?copy`、`?copyFrom`

`maeLoadCorners(filepath)` 接受文件路径但实际上不导入 corners（静默返回 nil）。

### 环境选项（模型文件）

```scheme
; 获取当前环境选项
maeGetEnvOption("TRAN")
maeGetEnvOption("TRAN" ?option "modelFiles")

; 设置模型文件
maeSetEnvOption("TRAN" ?options
  `(("modelFiles" (("/path/to/model.scs" "tt")))))
```

### 保存设置

```scheme
maeSaveSetup(?lib "myLib" ?cell "myCell" ?view "maestro" ?session "fnxSession4")
```

### 运行仿真

```scheme
; 异步——立即返回 "Interactive.N"
; GUI 保持响应，结果自动出现在 Maestro 窗口
maeRunSimulation()
maeRunSimulation(?session "fnxSession4")

; 单独等待（如果异步）
maeWaitUntilDone('All)
```

**重要：** `maeRunSimulation(?waitUntilDone t)` 阻塞 Virtuoso 的事件循环，这会阻止 GUI 刷新并可能破坏 bridge 连接。使用**异步** `maeRunSimulation()` + `maeWaitUntilDone('All)` 代替。

**重要：** 结果只有在 maestro 窗口通过 `deOpenCellView`**在运行前**打开时才会自动出现在 Maestro GUI 中。如果 maestro 仅作为后端会话（`maeOpenSetup`）打开，结果不会显示。

### 读取结果（程序化）

```scheme
; 打开特定的历史运行（为程序化访问设置结果指针）
maeOpenResults(?history "Interactive.2")

; 查询结果
maeGetResultTests()                    ; => ("AC" "TRAN")
maeGetResultOutputs(?testName "AC")    ; => ("Vout")

; 获取特定 corner 的输出值
maeGetOutputValue("maxOut" "TRAN2" ?cornerName "myCorner_2")
; => 0.6259399

; 检查规格状态
maeGetSpecStatus("maxOut" "TRAN2")
; => "fail"

; 导出所有结果到 CSV
maeExportOutputView(?fileName "/tmp/results.csv" ?view "Detail")

; 完成后关闭结果
maeCloseResults()
```

### 打开 Maestro 并显示历史结果

打开 maestro 视图并显示之前的仿真历史：

```python
lib, cell = "myLib", "myCell"

# 步骤 1：关闭所有现有会话（编辑模式是独占的）
r = client.execute_skill('maeGetSessions()')
for session in r.output.strip('()').replace('"', '').split():
    if session and session != 'nil':
        client.execute_skill(f'maeCloseSession(?session "{session}" ?forceClose t)')

# 步骤 2：通过仿真结果目录列出可用历史
#   路径：<simDir>/maestro/results/maestro/<historyName>/
#   用 getDirFiles 列出，过滤点前缀条目
r = client.execute_skill('asiGetResultsDir(asiGetCurrentSession())')
rd = r.output.strip('"')
base = re.match(r'(.*/maestro/results/maestro/)', rd).group(1)
r = client.execute_skill(f'getDirFiles("{base}")')
dirs = r.output.strip('()').replace('"', '').split()
histories = sorted([d for d in dirs if not d.startswith('.')])
latest = histories[-1]  # 例如 "Interactive.1"

# 步骤 3：打开 GUI + 设为可编辑 + 恢复历史 + 保存
client.execute_skill(f'deOpenCellView("{lib}" "{cell}" "maestro" "maestro" nil "r")')
client.execute_skill('maeMakeEditable()')
client.execute_skill(f'maeRestoreHistory("{latest}")')
client.execute_skill(f'maeSaveSetup(?lib "{lib}" ?cell "{cell}" ?view "maestro")')
```

关键点：
- **编辑模式是独占的**——只有一个会话可以拥有 cellview 的编辑模式。必须先通过 `maeCloseSession(?forceClose t)` 关闭所有现有会话。
- `deOpenCellView` 打开 GUI 窗口（最初是只读模式）。
- `maeMakeEditable()` 切换到编辑模式——**打开后立即调用**，在任何修改之前。否则关闭窗口会触发"保存更改？"对话框，这会死锁 SKILL 通道（只读无法保存，对话框阻塞一切）。
- `maeRestoreHistory("Interactive.N")` 将历史设为主动设置，使结果在 GUI 中可见。
- `maeSaveSetup` 持久化状态——**关闭前总是保存**。
- 历史名称**并不总是** `Interactive.N`——用户可以重命名。

### 工具函数

```scheme
; 将整个设置导出为可重现的 SKILL 脚本
maeWriteScript("mySetupScript.il")

; 为特定 corner 创建独立网表
maeCreateNetlistForCorner("TRAN2" "myCorner_2" "./myNetlistDir")

; 从 ADE L / ADE XL 迁移到 Maestro
maeMigrateADELStateToMaestro("myLib" "myCell" "spectre_state1")
maeMigrateADEXLToMaestro("myLib" "myCell" "adexl" ?maestroView "maestro_convert")
```

## 已知阻塞因素

- **GUI 对话框**阻塞 SKILL 执行通道。所有 `execute_skill()` 调用超时直到手动关闭对话框。常见原因："Specify history name"、"No analyses enabled"、"Change Mode Confirmation"。使用 `hiFormDone(hiGetCurrentForm())` 以编程方式关闭。
- **原理图必须检查并保存**（`schCheck` + `dbSave`）后才能仿真，否则网表生成失败并弹对话框。
- **原理图应在 GUI 中打开**，Maestro 才能正确引用它。
- **`maeOpenSetup` 创建后台编辑锁**——总是配对 `maeCloseSession(?forceClose t)`。陈旧的 `.cdslck` 文件可能需要手动删除。

## Pnoise Jitter Event——自动化限制

pnoise "jitter event" 表（Choosing Analyses → pnoise 中的 Add/Delete 按钮）**无法仅通过 SKILL API 完全自动化**。Add 按钮的内部函数 `_spectreRFAddJitterEvent` 存在，但需要 `asiSetAnalysisFieldVal` 无法设置的 Qt 小部件状态。

### 可行的操作

可以通过以下方式设置 pnoise 分析参数（频率范围、方法、触发节点）：
```python
client.execute_skill(f'maeSetAnalysis("{test}" "pnoise" ?enable t ?options `(...) ?session "{session}")')
```

**注意：** `maeGetAnalysis` 和 `maeSetAnalysis` 无需 `hiSetCurrentWindow` 即可工作。它们直接操作当前活动的 maestro 会话。两种语法都可以用于 `?options` 参数：反引号语法 `` `(("key" "val")) `` 和 `list(list("key" "val"))`。

`measTableData` 字段可以在内存中设置并持久化到 sdb：
```python
# 在内存中设置
client.execute_skill('asiSetAnalysisFieldVal(_pnAna "measTableData" \'("1;Edge Crossing;voltage;/X_DUT/LP;/X_DUT/LM;-;50m;1;rise;-;...")')
# 打开表单 + 应用以持久化
client.execute_skill('asiDisplayAnalysis(asiGetCurrentSession() "pnoise")')
client.execute_skill('hiFormApply(hiGetCurrentForm())')
client.execute_skill('hiFormDone(hiGetCurrentForm())')
client.execute_skill(f'maeSaveSetup(...)')
```

### 不行的操作

- `_spectreRFAddJitterEvent(asiGetCurrentAnalysisForm() 'pnoise "")`——函数存在但返回 nil，表保持空
- 仅通过 `asiSetAnalysisFieldVal` 设置 `measTableData` 而不表单 Apply——数据在内存中更新但不持久化到 sdb

### 当前最佳变通方法

从参考 maestro 复制 `active.state` 并替换实例路径：
```python
# active.state 是 XML——jitter events 存储在这里，不在 maestro.sdb 中
ssh(f"cp {src_maestro}/active.state {dst_maestro}/active.state")
ssh(f"sed -i 's|/I4/|/X_DUT/|g' {dst_maestro}/active.state")
```
然后关闭并重新打开 maestro 以从 `active.state` 加载。

### 已探索但失败的方法

| 方法 | 结果 |
|----------|--------|
| `_spectreRFAddJitterEvent` | 函数存在，返回 nil，表保持空 |
| `asiSetAnalysisFieldVal("measTableData" ...)` 单独 | 内存更新但不持久化 |
| `asiSetAnalysisFieldVal` + `hiFormApply` | 持久化到 sdb 但 GUI 表可能不显示 |
| `maeSetAnalysis` 带 measTableData 选项 | 内存更新但不持久化 |
| 表单字段 `->value =` + `_spectreRFAddJitterEvent` | Qt 小部件未从 SKILL 同步 |
| `_spectreRFDeleteJitterEvent` | **可行**——可以删除现有事件 |

### 关键文件

- `maestro/active.state`——包含 jitter event 数据的 XML 文件（不在 `maestro.sdb` 中）
- `maestro/maestro.sdb`——包含 maestro 设置的 XML 文件（测试、分析、输出、变量）
- 两者都是基于文本的 XML，可以用 `sed` 编辑

## 读取结果——OCEAN API

所有 OCEAN 函数都内置在 CIW 中。无需单独加载。

```python
results_dir = client.execute_skill(
    'asiGetResultsDir(asiGetCurrentSession())'
).output.strip('"')
client.execute_skill(f'openResults("{results_dir}")')
client.execute_skill('selectResults("ac")')
client.execute_skill('outputs()')
client.execute_skill('sweepNames()')

# 导出波形到文本
client.execute_skill(
    'ocnPrint(dB20(mag(v("/OUT"))) ?numberNotation (quote scientific) '
    '?numSpaces 1 ?output "/tmp/ac_db.txt")'
)
client.download_file('/tmp/ac_db.txt', Path('output/ac_db.txt'))
```

## OCEAN 快速参考

| 函数 | 用途 |
|----------|---------|
| `openResults(dir)` | 打开 PSF 结果目录 |
| `selectResults(analysis)` | 选择分析类型 |
| `outputs()` | 列出可用信号名称 |
| `sweepNames()` | 列出扫描变量名称 |
| `v(signal)` | 获取电压波形对象 |
| `ocnPrint(wave ?output path)` | 导出波形到文本文件 |
| `value(wave time)` | 获取特定时间的值 |

## 完整 Maestro 工作流程（Python）

```python
client = VirtuosoClient.from_env()

# 1. 在 GUI 中打开原理图（必需！）
client.open_window(lib, cell, view="schematic")

# 2. 打开/创建 maestro
r = client.execute_skill(f'maeOpenSetup("{lib}" "{cell}" "maestro")')
session = r.output.strip('"')

# 3. 创建测试 + 分析
client.execute_skill(
    f'maeCreateTest("AC" ?lib "{lib}" ?cell "{cell}" '
    f'?view "schematic" ?simulator "spectre" ?session "{session}")')
client.execute_skill(
    f'maeSetAnalysis("AC" "tran" ?enable nil ?session "{session}")')
client.execute_skill(
    f'maeSetAnalysis("AC" "ac" ?enable t '
    f'?options `(("start" "1") ("stop" "10G") ("dec" "20")) '
    f'?session "{session}")')

# 4. 添加输出 + 变量
client.execute_skill(
    f'maeAddOutput("Vout" "AC" ?outputType "net" '
    f'?signalName "/OUT" ?session "{session}")')
client.execute_skill(f'maeSetVar("c_val" "1p,100f" ?session "{session}")')

# 5. 保存 + 运行（异步——永不使用 ?waitUntilDone t，它会阻塞事件循环）
client.execute_skill(
    f'maeSaveSetup(?lib "{lib}" ?cell "{cell}" '
    f'?view "maestro" ?session "{session}")')
client.execute_skill(f'maeRunSimulation(?session "{session}")')
client.execute_skill("maeWaitUntilDone('All)", timeout=300)

# 6. 导出结果
client.execute_skill(
    'maeExportOutputView(?fileName "/tmp/results.csv" ?view "Detail")')
client.download_file('/tmp/results.csv', 'output/results.csv')
```

## 示例

- `examples/01_virtuoso/maestro/01_read_open_maestro.py`——从打开的 maestro 读取配置
- `examples/01_virtuoso/maestro/02_gui_open_read_close_maestro.py`——GUI 打开 → 读取配置 → 关闭
- `examples/01_virtuoso/maestro/03_bg_open_read_close_maestro.py`——后台打开 → 读取配置 → 关闭
- `examples/01_virtuoso/maestro/04_read_env.py`——读取环境设置
- `examples/01_virtuoso/maestro/05_read_results.py`——读取仿真结果
- `examples/01_virtuoso/maestro/06a_rc_create.py`——创建 RC 原理图 + Maestro 设置
- `examples/01_virtuoso/maestro/06b_rc_simulate.py`——运行仿真
- `examples/01_virtuoso/maestro/06c_rc_read_results.py`——读取结果、导出波形、打开 GUI

## axl* API——变量管理

`axl*` 函数直接操作 Maestro 设置数据库。用于删除 `maeDeleteVar` 无法触及的测试级变量。

```scheme
; 获取设置数据库句柄
axlGetMainSetupDB("fnxSession1")         ; => 7918（整数句柄）

; 获取测试句柄
axlGetTest(axlGetMainSetupDB("fnxSession1") "IB_PSS")   ; => 7936

; 从测试获取变量元素
axlGetVar(axlGetTest(axlGetMainSetupDB("fnxSession1") "IB_PSS") "f")  ; => 7958

; 删除测试级变量
axlRemoveElement(axlGetVar(axlGetTest(axlGetMainSetupDB("fnxSession1") "IB_PSS") "f"))
; => t

; 删除全局变量
axlRemoveElement(axlGetVar(axlGetMainSetupDB("fnxSession1") "f"))
```

**注意：** 要删除全局变量，必须首先删除所有具有本地副本的测试中的变量。对每个测试使用 `axlGetTest` + `axlGetVar` + `axlRemoveElement`，然后删除全局变量。

## 另见

- `references/maestro-python-api.md`——Python API 参考（会话、读取器、写入器）
