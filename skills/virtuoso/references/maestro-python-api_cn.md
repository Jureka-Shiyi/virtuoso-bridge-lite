# Maestro Python API

Cadence Maestro（ADE Assembler）SKILL 函数的 Python 封装。

**包：** `virtuoso_bridge.virtuoso.maestro`

```python
from virtuoso_bridge import VirtuosoClient
from virtuoso_bridge.virtuoso.maestro import open_session, close_session, read_config
```

## 两种会话模式

| | 后台（`open_session`） | GUI（`deOpenCellView`） |
|---|---|---|
| 锁文件 | 创建 `.cdslck` | 创建 `.cdslck` |
| 读取配置 | 是 | 是 |
| 写入配置 | 是 | 是（需要 `maeMakeEditable`） |
| 运行仿真 | 可以启动，但 `close_session` 会取消 | 是 |
| `wait_until_done` | 立即返回（不等待） | 阻塞直到完成 |
| 关闭 | `close_session` → 锁删除 | `hiCloseWindow` |

**后台用于读取/写入配置。GUI 用于仿真。**

## 会话管理

`maestro/session.py`

| Python | SKILL | 描述 |
|--------|-------|------|
| `open_session(client, lib, cell) -> str` | `maeOpenSetup` | 后台打开，返回会话字符串 |
| `close_session(client, session)` | `maeCloseSession` | 后台关闭 |
| `find_open_session(client) -> str \| None` | `maeGetSessions` + `maeGetSetup` | 查找第一个带有效测试的活动会话 |

```python
session = open_session(client, "PLAYGROUND_AMP", "TB_AMP_5T_D2S_DC_AC")
# ... 做工作 ...
close_session(client, session)
```

## 读取——三个独立函数

`maestro/reader.py`

所有函数返回 `dict[str, tuple[str, str]]`，其中 key = 标签，value = `(skill_expr, raw_output)`。

### read_config——测试设置

| 键 | SKILL |
|-----|-------|
| `maeGetSetup` | `maeGetSetup(?session session)` |
| `maeGetEnabledAnalysis` | `maeGetEnabledAnalysis(test ?session session)` |
| `maeGetAnalysis:<name>` | `maeGetAnalysis(test name ?session session)`——每个启用的分析一个 |
| `maeGetTestOutputs` | `maeGetTestOutputs(test ?session session)`——返回 `(name type signal expression)` |
| `variables` | `maeGetSetup(?session session ?typeName "variables")` |
| `parameters` | `maeGetSetup(?session session ?typeName "parameters")` |
| `corners` | `maeGetSetup(?session session ?typeName "corners")` |

### read_env——系统设置

| 键 | SKILL |
|-----|-------|
| `maeGetEnvOption` | `maeGetEnvOption(test ?session session)`——模型文件、视图列表等 |
| `maeGetSimOption` | `maeGetSimOption(test ?session session)`——reltol、temp、gmin 等 |
| `maeGetCurrentRunMode` | `maeGetCurrentRunMode(?session session)` |
| `maeGetJobControlMode` | `maeGetJobControlMode(?session session)` |
| `maeGetSimulationMessages` | `maeGetSimulationMessages(?session session)` |

### read_results——仿真结果

| 键 | SKILL |
|-----|-------|
| `maeGetResultTests` | `maeGetResultTests()` |
| `maeGetOutputValues` | SKILL 循环：`maeGetOutputValue` + `maeGetSpecStatus` 对每个输出 |
| `maeGetOverallSpecStatus` | `maeGetOverallSpecStatus()` |
| `maeGetOverallYield` | `maeGetOverallYield(history)` |

历史名称从 `asiGetResultsDir` 自动检测。无结果时返回空字典。

### export_waveform——下载波形数据

| Python | SKILL / OCEAN |
|--------|---------------|
| `export_waveform(client, session, expression, local_path, *, analysis="ac", history="")` | `maeOpenResults` → `selectResults` → `ocnPrint` → `maeCloseResults` |

对于返回 `"wave"` 而不是标量的输出。将波形下载为文本文件（freq/time vs value）。

```python
session = open_session(client, "PLAYGROUND_AMP", "TB_AMP_5T_D2S_DC_AC")

# 读取配置
for key, (expr, raw) in read_config(client, session).items():
    print(f"[{key}] {expr}")
    print(raw)

# 读取环境
for key, (expr, raw) in read_env(client, session).items():
    print(f"[{key}] {expr}")
    print(raw)

# 读取结果
for key, (expr, raw) in read_results(client, session).items():
    print(f"[{key}] {expr}")
    print(raw)

# 导出波形
export_waveform(client, session,
    'dB20(mag(VF("/VOUT") / VF("/VSIN")))',
    "output/gain_db.txt", analysis="ac")

export_waveform(client, session,
    'getData("out" ?result "noise")',
    "output/noise.txt", analysis="noise")

close_session(client, session)
```

## 写入——测试

`maestro/writer.py`

| Python | SKILL | 描述 |
|--------|-------|------|
| `create_test(client, test, *, lib, cell, view="schematic", simulator="spectre", session="")` | `maeCreateTest` | 创建新测试 |
| `set_design(client, test, *, lib, cell, view="schematic", session="")` | `maeSetDesign` | 更改现有测试的 DUT |

```python
create_test(client, "TRAN2", lib="myLib", cell="myCell")
set_design(client, "TRAN2", lib="myLib", cell="newCell")
```

## 写入——分析

| Python | SKILL | 描述 |
|--------|-------|------|
| `set_analysis(client, test, analysis, *, enable=True, options="", session="")` | `maeSetAnalysis` | 启用/禁用分析，设置选项 |

```python
# 启用 transient，stop=60n
set_analysis(client, "TRAN2", "tran", options='(("stop" "60n") ("errpreset" "conservative"))')

# 启用 AC
set_analysis(client, "TRAN2", "ac", options='(("start" "1") ("stop" "10G") ("dec" "20"))')

# 禁用 tran
set_analysis(client, "TRAN2", "tran", enable=False)
```

## 写入——输出和规格

| Python | SKILL | 描述 |
|--------|-------|------|
| `add_output(client, name, test, *, output_type="", signal_name="", expr="", session="")` | `maeAddOutput` | 添加波形或表达式输出 |
| `set_spec(client, name, test, *, lt="", gt="", session="")` | `maeSetSpec` | 设置通过/失败规格 |

```python
# 波形输出
add_output(client, "OutPlot", "TRAN2", output_type="net", signal_name="/OUT")

# 表达式输出
add_output(client, "maxOut", "TRAN2", output_type="point", expr='ymax(VT("/OUT"))')

# 规格：maxOut < 400mV
set_spec(client, "maxOut", "TRAN2", lt="400m")

# 规格：BW > 1GHz
set_spec(client, "BW", "AC", gt="1G")
```

## 写入——变量

| Python | SKILL | 描述 |
|--------|-------|------|
| `set_var(client, name, value, *, type_name="", type_value="", session="")` | `maeSetVar` | 设置全局变量或 corner 扫描 |
| `get_var(client, name, *, session="")` | `maeGetVar` | 获取变量值 |

```python
set_var(client, "vdd", "1.35")
get_var(client, "vdd")  # => '"1.35"'

# Corner 扫描
set_var(client, "vdd", "1.2 1.4", type_name="corner", type_value='("myCorner")')
```

## 写入——参数（参数扫描）

| Python | SKILL | 描述 |
|--------|-------|------|
| `get_parameter(client, name, *, type_name="", type_value="", session="")` | `maeGetParameter` | 读取参数值 |
| `set_parameter(client, name, value, *, type_name="", type_value="", session="")` | `maeSetParameter` | 添加/更新参数 |

```python
set_parameter(client, "cload", "1p")
set_parameter(client, "cload", "1p 2p", type_name="corner", type_value='("myCorner")')
```

## 写入——环境和仿真器选项

| Python | SKILL | 描述 |
|--------|-------|------|
| `set_env_option(client, test, options, *, session="")` | `maeSetEnvOption` | 设置模型文件、视图列表等 |
| `set_sim_option(client, test, options, *, session="")` | `maeSetSimOption` | 设置 reltol、temp、gmin 等 |

```python
# 更改模型文件 section
set_env_option(client, "TRAN2",
    '(("modelFiles" (("/path/model.scs" "ff"))))')

# 更改温度
set_sim_option(client, "TRAN2", '(("temp" "85"))')
```

## 写入——Corners

| Python | SKILL | 描述 |
|--------|-------|------|
| `set_corner(client, name, *, disable_tests="", session="")` | `maeSetCorner` | 创建/修改 corner |
| `load_corners(client, filepath, *, sections="corners", operation="overwrite")` | `maeLoadCorners` | 从 CSV 加载 corners |

```python
set_corner(client, "myCorner", disable_tests='("AC" "TRAN")')
load_corners(client, "my_corners.csv")
```

## 写入——运行模式和任务控制

| Python | SKILL | 描述 |
|--------|-------|------|
| `set_current_run_mode(client, run_mode, *, session="")` | `maeSetCurrentRunMode` | 切换运行模式 |
| `set_job_control_mode(client, mode, *, session="")` | `maeSetJobControlMode` | 设置 Local/LSF 等 |
| `set_job_policy(client, policy, *, test_name="", job_type="", session="")` | `maeSetJobPolicy` | 设置任务策略 |

```python
set_current_run_mode(client, "Single Run, Sweeps and Corners")
set_job_control_mode(client, "Local")
```

## 写入——仿真

| Python | SKILL | 描述 |
|--------|-------|------|
| `run_simulation(client, *, session="")` | `maeRunSimulation` | 运行（异步） |
| `wait_until_done(client, timeout=300)` | `maeWaitUntilDone` | 阻塞直到完成 |

```python
run_simulation(client)
wait_until_done(client, timeout=600)
```

## 写入——导出

| Python | SKILL | 描述 |
|--------|-------|------|
| `create_netlist_for_corner(client, test, corner, output_dir)` | `maeCreateNetlistForCorner` | 为一个 corner 导出网表 |
| `export_output_view(client, filepath, *, view="Detail")` | `maeExportOutputView` | 导出结果到 CSV |
| `write_script(client, filepath)` | `maeWriteScript` | 将设置导出为 SKILL 脚本 |

```python
create_netlist_for_corner(client, "TRAN2", "myCorner_2", "./myNetlistDir")
export_output_view(client, "./results.csv")
write_script(client, "mySetupScript.il")
```

## 写入——迁移

| Python | SKILL | 描述 |
|--------|-------|------|
| `migrate_adel_to_maestro(client, lib, cell, state)` | `maeMigrateADELStateToMaestro` | ADE L → Maestro |
| `migrate_adexl_to_maestro(client, lib, cell, view="adexl", *, maestro_view="maestro")` | `maeMigrateADEXLToMaestro` | ADE XL → Maestro |

```python
migrate_adel_to_maestro(client, "myLib", "myCell", "spectre_state1")
migrate_adexl_to_maestro(client, "myLib", "myCell")
```

## 写入——保存

| Python | SKILL | 描述 |
|--------|-------|------|
| `save_setup(client, lib, cell, *, session="")` | `maeSaveSetup` | 保存 maestro 到磁盘 |

```python
save_setup(client, "myLib", "myCell", session=session)
```
